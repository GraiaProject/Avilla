from __future__ import annotations

from collections import ChainMap
from contextlib import AsyncExitStack
from inspect import isclass
from typing import (
    TYPE_CHECKING,
    Any,
    AsyncIterator,
    Callable,
    Generic,
    Iterable,
    TypeVar,
    cast,
    overload,
)

from graia.amnesia.message import Element, MessageChain
from typing_extensions import Unpack

from avilla.core.account import AbstractAccount
from avilla.core.action import Action, MessageSend, StandardActionImpl
from avilla.core.action.extension import ActionExtension
from avilla.core.action.middleware import ActionMiddleware
from avilla.core.context import ctx_relationship
from avilla.core.metadata.model import (
    CellCompose,
    CellOf,
    Metadata,
    MetadataModifies,
    Ts,
)
from avilla.core.resource import Resource, get_provider
from avilla.core.utilles.selector import DynamicSelector, Selectable, Selector

if TYPE_CHECKING:
    from avilla.core.message import Message
    from avilla.core.protocol import BaseProtocol


_A = TypeVar("_A", bound=Action)
_A2 = TypeVar("_A2", bound=Action)


class RelationshipExecutor(Generic[_A]):
    relationship: Relationship
    action: _A
    middlewares: list[ActionMiddleware]
    extensions: dict[str, list[ActionExtension]]
    _oneof_groups: set[str]

    _target: Selector | None = None

    def __init__(self, relationship: Relationship) -> None:
        self.relationship = relationship
        self.middlewares = relationship.protocol.action_middlewares + relationship.protocol.avilla.action_middlewares
        self.extensions = {}
        self._impl_cache = ChainMap(
            self.relationship.protocol.extension_impls, self.relationship.avilla.extension_impls
        )
        self._oneof_groups = set()

    def __await__(self):
        return self.__await_impl__().__await__()

    async def __await_impl__(self):
        async with AsyncExitStack() as stack:
            for middleware in reversed(self.middlewares):
                await stack.enter_async_context(middleware.lifespan(self))
            for executor_class in self.relationship.protocol.action_executors:
                # 需要注意: 我们直接从左往右迭代了, 所以建议 full > exist long > exist short > None
                if executor_class.pattern is None or (
                    self._target is not None and executor_class.pattern.match(self._target)
                ):
                    executor = executor_class(self.relationship.protocol)
                    implement = executor.get_implement(self.action)
                    if isclass(implement) and issubclass(implement, StandardActionImpl):
                        return await self.execute_standard(implement)
                    assert not isinstance(implement, type)
                    return await implement(executor, self.action, self.relationship)
            if self._target is not None:
                raise NotImplementedError(
                    f"No action executor found for {self.action.__class__.__name__}, target for {self._target.path}"
                )
            else:
                raise NotImplementedError(f"No action executor found for {self.action.__class__.__name__}")

    def get_extension_impl(self, ext: ActionExtension, std: type[StandardActionImpl] | None):
        if std is None:
            return self._impl_cache.get(type(ext))
        return self._impl_cache.copy().new_child(std.extension_impls).get(type(ext))

    async def execute_standard(self, std: type[StandardActionImpl]):
        for middleware in reversed(self.middlewares):
            await middleware.before_execute(self)

        params = await std.get_execute_params(self)

        for middleware in reversed(self.middlewares):
            await middleware.before_extensions_apply(self, params)

        for group, extensions in self.extensions.items():
            if group in self._oneof_groups:
                for ext in extensions:
                    if (impl := self.get_extension_impl(ext, std)) is not None:
                        await impl(self, ext, params)
                        break
                else:
                    raise NotImplementedError(
                        f"No available extension impl found for {std.__name__} in group {group}:{extensions}"
                    )
            else:
                for ext in extensions:
                    impl = self.get_extension_impl(ext, std)
                    if impl is None:
                        raise NotImplementedError(f"No available extension impl found for {type(ext).__name__}")
                    await impl(self, ext, params)

        for middleware in reversed(self.middlewares):
            await middleware.on_params_ready(self, params)

        return std.unwarp_result(self, await self.relationship.current.call(std.endpoint, params))

    def act(self, action: _A2) -> RelationshipExecutor[_A2]:
        self._target = action.set_default_target(self.relationship)
        self.action = action
        return self  # type: ignore

    __call__ = act

    def to(self, target: Selector):
        self.action.set_target(target)
        self._target = target
        return self

    def use(self, *middleware: ActionMiddleware):
        self.middlewares.extend(middleware)
        return self

    def ext(self, group: str, extensions: list[ActionExtension], *, oneof: bool = False):
        self.extensions[group] = extensions
        if oneof:
            self._oneof_groups.add(group)
        return self


class RelationshipQuerier:
    relationship: Relationship
    target: Selector

    def __init__(self, relationship: Relationship) -> None:
        self.relationship = relationship
        self.target = self.relationship.ctx

    def __await__(self):
        return self.__await_impl__()

    @staticmethod
    def generate_with_specified(k: str, v: str):
        async def real_generator(upper: AsyncIterator[Selector] | None = None):
            if upper is None:
                yield Selector().from_dict({k: v})
                return
            async for upper_value in upper:
                a = upper_value.copy()
                a.pattern[k] = v
                yield a

        return real_generator

    async def generate_from_upper(self, depth: Selector, upper: AsyncIterator[Selector] | None = None):
        depth_keys = list(depth.pattern.keys())
        if not depth_keys:
            return
        current = depth_keys[-1]
        past = ".".join(depth_keys[:-1])
        if depth_keys[0] != "land":
            depth.pattern = {"land": self.relationship.land.name, **depth.pattern}
        for querier in self.relationship.protocol.query_handlers:
            if querier.prefix is None or querier.prefix == past:
                querier = querier(self.relationship.protocol)
                break
        else:
            raise NotImplementedError(f"No query handler found for {past}")
        if current not in querier.queriers:
            raise NotImplementedError(f"No querier found for {past}, {current} unimplemented")
        if upper is None:
            async for current_value in querier.queriers[current](
                querier, self.relationship, Selector().land(self.relationship.land), depth.match
            ):
                yield current_value
            return
        async for upper_value in upper:
            async for current_value in querier.queriers[current](querier, self.relationship, upper_value, depth.match):
                yield current_value

    async def __await_impl__(self):
        if self.target.empty:
            raise ValueError("Selector is empty.")
        past: dict[str, str | Callable[[str], bool]] = {}
        stack: list[AsyncIterator[Selector]] = []

        for key, value in self.target.pattern.items():
            if key == "land":
                continue
            past[key] = value
            current_pattern = DynamicSelector()
            current_pattern.pattern = past.copy()
            if isinstance(value, str):
                # 当前层级是明确的, 那么就只需要给 upper 上每个值加上当前层级.
                # 如果 past 为空, 则直接返回.
                stack.append(self.generate_with_specified(key, value)(stack[-1] if stack else None))
            else:
                stack.append(self.generate_from_upper(current_pattern, stack[-1] if stack else None))

        async for i in stack[-1]:
            yield i

    def query(self, selector: Selector) -> RelationshipQuerier:
        self.target = selector
        return self  # type: ignore

    __call__ = query


_T = TypeVar("_T")
_M = TypeVar("_M", bound=Metadata)


class Relationship:
    ctx: Selector
    mainline: Selector
    current: AbstractAccount
    cache: dict[str, Any]
    via: Selector | None = None

    protocol: "BaseProtocol"

    _middlewares: list[ActionMiddleware]

    def __init__(
        self,
        protocol: "BaseProtocol",
        ctx: Selector,
        mainline: Selector,
        current: AbstractAccount,
        via: Selector | None = None,
        middlewares: list[ActionMiddleware] | None = None,
    ) -> None:
        self.ctx = ctx
        self.mainline = mainline
        self.via = via
        self.current = current
        self.protocol = protocol
        self._middlewares = middlewares or []
        self.cache = {}

    @property
    def exec(self):
        return RelationshipExecutor(self)

    @property
    def query(self):
        return RelationshipQuerier(self)

    @property
    def avilla(self):
        return self.protocol.avilla

    @property
    def land(self):
        return self.protocol.land

    def complete(self, selector: Selector):
        rules = self.protocol.completion_rules.get(self.mainline.path) or {}
        rules = (self.protocol.completion_rules.get("_") or {}) | rules
        if selector.path in rules:
            return selector.mixin(rules[selector.path], self.mainline, self.ctx, *((self.via,) if self.via else ()))

        if "land" not in selector.pattern:
            selector = selector.copy()
            selector.pattern = {"land": self.land.name, **selector.pattern}
        return selector

    async def fetch(self, resource: Resource[_T]) -> _T:
        with ctx_relationship.use(self):
            provider = get_provider(resource, self)
            if provider is None:
                raise ValueError(f"{type(resource)} is not a supported resource.")
            return await provider.fetch(resource, self)

    def send_message(
        self, message: MessageChain | str | Iterable[str | Element], *, reply: Message | Selector | str | None = None
    ):
        return self.exec.act(MessageSend(message, reply=reply))

    @overload
    async def check(self) -> None:
        # 检查 Relationship 的存在性.
        # 如 Relationship 的存在性无法被验证为真, 则 Relationship 不成立, 抛出错误.
        ...

    @overload
    async def check(self, target: Selector, strict: bool = False) -> bool:
        # 检查 target 相对于当前关系 Relationship 的存在性.
        # 注意, 这里是 "相对于当前关系", 如 Github 的项目若为 Private, 则对于外界/Amonymous来说是不存在的, 即使他从客观上是存在的.
        # 注意, target 不仅需要相对于当前关系是存在的, 由于关系本身处在一个 mainline 之中,
        # mainline 相当于工作目录或者是 docker 那样的应用容器, 后者是更严谨的比喻,
        # 因为有些操作**只能**在处于一个特定的 mainline 中才能完成, 这其中包含了访问并操作某些 target.
        # 在 strict 模式下, target 被视作包含 "仅在当前 mainline 中才能完成的操作" 的集合中,
        # 表示其访问或是操作必须以当前 mainline 甚至是 current(account) 为基础.
        # 如果存在可能的 via, 则会先检查 via 的存在性, 因为 via 是维系这段关系的基础.
        ...

    async def check(self, target: Selector | None = None, strict: bool = False) -> bool | None:
        ...

    @property
    def is_resource(self) -> bool:
        return self.ctx.path_without_land in self.protocol.resource_labels

    @overload
    async def meta(self, operator: MetadataModifies[_T], /) -> _T:
        ...

    @overload
    async def meta(self, target: Any, operator: MetadataModifies[_T], /) -> _T:
        ...

    @overload
    async def meta(self, operator: type[_M], /, *, flush: bool = False) -> _M:
        ...

    @overload
    async def meta(self, target: Any, operator: type[_M], /, *, flush: bool = False) -> _M:
        ...

    @overload
    async def meta(self, operator: CellOf[Unpack[tuple[Any, ...]], _M], /, *, flush: bool = False) -> _M:
        ...

    @overload
    async def meta(self, target: Any, operator: CellOf[Unpack[tuple[Any, ...]], _M], /, *, flush: bool = False) -> _M:
        ...

    @overload
    async def meta(self, operator: CellCompose[Unpack[Ts]], /, *, flush: bool = False) -> tuple[Unpack[Ts]]:
        ...

    @overload
    async def meta(
        self, target: Any, operator: CellCompose[Unpack[Ts]], /, *, flush: bool = False
    ) -> tuple[Unpack[Ts]]:
        ...

    async def meta(self, op_or_target: Any, maybe_op: Any = None, /, *, flush: bool = False) -> Any:
        op, target = cast(
            tuple["type[_M] | MetadataModifies[_T] | CellOf[Unpack[tuple[Any, ...]], _M]", Any],
            (op_or_target, None) if maybe_op is None else (maybe_op, op_or_target),
        )
        with ctx_relationship.use(self):
            if isinstance(op, (CellOf, CellCompose)) or isinstance(op, type) and issubclass(op, Metadata):
                modify = None
                model = op
            elif isinstance(op, MetadataModifies):
                modify = op
                model = op.model
            else:
                raise TypeError(f"{op_or_target} & {maybe_op} is not a supported metadata operation for rs.meta.")

            target = target or model.get_default_target(self)

            if target is None:
                raise ValueError(
                    f"{model}'s modify is not a supported metadata for rs.meta, which requires a categorical target."
                )
            if result := self.cache.get("meta", {}).get(target, {}).get(op, None):
                if flush:
                    del self.cache["meta"][target][op]
                else:
                    return result
            if isinstance(target, Selector):
                if isinstance(target, DynamicSelector):
                    raise TypeError(f"Use rs.query for dynamic selector {target}!")
                target_ref = target
            elif not isinstance(target, Selectable):
                raise ValueError(f"{target} is not a supported target for rs.meta, which requires to be selectable.")
            else:
                target_ref = target.to_selector()
            if isinstance(target, Resource):
                provider = get_provider(target, self)
                if provider is None:
                    raise ValueError(f"cannot find a valid provider for resource {target} to use rs.meta")
                source = provider.get_metadata_source()
            else:
                source = self.protocol.get_metadata_provider(target_ref)

            if source is None:
                if modify is None:
                    raise ValueError(
                        f"{model} is not a supported metadata at present, which not ordered by any source."
                    )
                raise ValueError(
                    f"{model}'s modify is not a supported metadata at present, which not ordered by any source."
                )

            if modify is None:
                result = await source.fetch(target, model)
                self.cache.setdefault("meta", {}).setdefault(target, {})[op] = result
                return result
            return cast(_T, await source.modify(target, cast(MetadataModifies[Selector], modify)))
