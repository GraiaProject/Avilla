from __future__ import annotations

from contextlib import AsyncExitStack, suppress
from inspect import isfunction
from typing import TYPE_CHECKING, Any, AsyncIterator, Iterable, TypeVar, cast, overload

from avilla.core.action import Action  # ?
from avilla.core.context import ctx_relationship
from avilla.core.metadata.model import Metadata, MetadataModifies
from avilla.core.resource import Resource, get_provider
from avilla.core.typing import ActionMiddleware
from avilla.core.utilles.selector import DynamicSelector, Selector, Summarizable

if TYPE_CHECKING:
    from avilla.core.protocol import BaseProtocol


class RelationshipExecutor:
    relationship: Relationship
    action: Action
    middlewares: list[ActionMiddleware]

    _target: Selector | None = None

    def __init__(self, relationship: Relationship) -> None:
        self.relationship = relationship
        self.middlewares = relationship.protocol.action_middlewares + relationship.protocol.avilla.action_middlewares

    def __await__(self):
        return self.__await_impl__().__await__()

    async def __await_impl__(self):
        async with AsyncExitStack() as stack:
            for middleware in reversed(self.middlewares):
                await stack.enter_async_context(middleware(self))
            for executor in self.relationship.protocol.action_executors:
                # 需要注意: 我们直接从左往右迭代了, 所以建议 full > exist long > exist short > None
                if executor.pattern is None:
                    return await executor(self.relationship.protocol).execute(self.relationship, self.action)
                elif self._target is not None and executor.pattern.match(self._target):
                    return await executor(self.relationship.protocol).execute(self.relationship, self.action)
            if self._target is not None:
                raise NotImplementedError(
                    f"No action executor found for {self.action.__class__.__name__}, target for {self._target.path}"
                )
            else:
                raise NotImplementedError(f"No action executor found for {self.action.__class__.__name__}")

    def execute(self, action: Action):
        self._target = action.set_default_target(self.relationship)
        self.action = action
        return self

    __call__ = execute

    def to(self, target: Selector):
        self.action.set_target(target)
        self._target = target
        return self

    def use(self, *middleware: ActionMiddleware):
        self.middlewares.extend(middleware)
        return self


_T = TypeVar("_T")
_M = TypeVar("_M", bound=Metadata)


async def _as_asynciter(iterable: Iterable[_T]) -> AsyncIterator[_T]:
    for i in iterable:
        yield i


class Relationship:
    ctx: Selector
    mainline: Selector
    current: Selector
    via: Selector | None = None

    protocol: "BaseProtocol"

    _middlewares: list[ActionMiddleware]

    def __init__(
        self,
        protocol: "BaseProtocol",
        ctx: Selector,
        mainline: Selector,
        current: Selector,
        via: Selector | None = None,
        middlewares: list[ActionMiddleware] | None = None,
    ) -> None:
        self.ctx = ctx
        self.mainline = mainline
        self.via = via
        self.current = current
        self.protocol = protocol
        self._middlewares = middlewares or []

    @property
    def exec(self):
        return RelationshipExecutor(self)

    @property
    def avilla(self):
        return self.protocol.avilla

    @property
    def land(self):
        return self.protocol.land

    @property
    def account(self):
        account = self.avilla.get_account(selector=self.current)
        assert account is not None
        return account

    def complete(self, selector: Selector):
        rules = self.protocol.completion_rules.get(selector.path)
        if rules is None:
            return selector
        for alternative in rules:
            with suppress(ValueError):
                return selector.mixin(
                    alternative, self.ctx, self.mainline, *((self.via,) if self.via is not None else ())
                )
        return selector

    async def fetch(self, resource: Resource[_T]) -> _T:
        with ctx_relationship.use(self):
            provider = get_provider(resource, self)
            if provider is None:
                raise ValueError(f"{type(resource)} is not a supported resource.")
            return await provider.fetch(resource, self)

    async def query(self, selector: Selector):
        if selector.empty:
            raise ValueError("Selector is empty.")
        past = {}
        stack: list[AsyncIterator[Selector]] = []

        def generate_with_specified(k, v):
            async def real_generator(upper: AsyncIterator[Selector] | None = None):
                if upper is None:
                    yield Selector().from_dict({k: v})
                    return
                async for upper_value in upper:
                    a = upper_value.copy()
                    a.pattern[k] = v
                    yield a

            return real_generator

        async def generate_from_upper(depth: Selector, upper: AsyncIterator[Selector] | None = None):
            current = list(depth.pattern.keys())[-1]
            past = ".".join(list(depth.pattern.keys())[:-1])
            for querier in self.protocol.protocol_query_handlers:
                if querier.prefix is None or querier.prefix == past:
                    querier = querier(self.protocol)
                    break
            else:
                raise NotImplementedError(f"No query handler found for {past}")
            if current not in querier.queriers:
                raise NotImplementedError(f"No querier found for {past}, {current} unimplemented")
            if depth.pattern and list(depth.pattern.keys())[0] != "land":
                depth.pattern = {"land": self.land.name, **depth.pattern}
            if upper is None:
                async for current_value in querier.queriers[current](
                    querier, self, Selector().land(self.land), depth.match
                ):
                    yield current_value
                return
            async for upper_value in upper:
                async for current_value in querier.queriers[current](querier, self, upper_value, depth.match):
                    yield current_value

        for key, value in selector.pattern.items():
            if key == "land":
                continue
            past[key] = value
            current_pattern = DynamicSelector()
            current_pattern.pattern = past.copy()
            if isinstance(value, str):
                # 当前层级是明确的, 那么就只需要给 upper 上每个值加上当前层级.
                # 如果 past 为空, 则直接返回.
                stack.append(generate_with_specified(key, value)(stack[-1] if stack else None))
            else:
                stack.append(generate_from_upper(current_pattern, stack[-1] if stack else None))
        async for i in stack[-1]:
            yield i

    @overload
    async def meta(self, op_or_target: type[_M]) -> _M:
        ...

    @overload
    async def meta(self, op_or_target: MetadataModifies[_T]) -> _T:
        ...

    @overload
    async def meta(self, op_or_target: Any, op: type[_M]) -> _M:
        ...

    @overload
    async def meta(self, op_or_target: Any, op: MetadataModifies[_T]) -> _T:
        ...

    async def meta(
        self,
        op_or_target: type[_M] | MetadataModifies[_T] | Any,
        op: type[_M] | MetadataModifies[_T] | None = None,
    ) -> _M | _T:
        with ctx_relationship.use(self):
            op, target = cast(
                "tuple[type[_M] | MetadataModifies[_T], Any]",
                (op_or_target, None if op is None else op, op_or_target),
            )

            if isinstance(op, type) and issubclass(op, Metadata):
                modify = None
                model = op
            elif isinstance(op, MetadataModifies):
                modify = op
                model = op.model
            else:
                raise TypeError(f"{op_or_target} & {op} is not a supported metadata operation for rs.meta.")

            target = target or model.get_default_target(self)

            if target is None:
                raise ValueError(
                    f"{model}'s modify is not a supported metadata for rs.meta, which requires a categorical target."
                )
            if not isinstance(target, Summarizable):
                raise ValueError(
                    f"{target} is not a supported target for rs.meta, which requires a summarizable trait."
                )

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
                return await source.fetch(target, model)
            return cast(_T, await source.modify(target, cast(MetadataModifies[Selector], modify)))
