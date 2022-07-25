from __future__ import annotations

from contextlib import AsyncExitStack, suppress
from inspect import isfunction
from typing import TYPE_CHECKING, Any, AsyncIterator, Iterable, TypeVar, cast, overload

from avilla.core.context import ctx_relationship
from avilla.core.metadata.model import Metadata, Modify
from avilla.core.resource import Resource, get_provider
from avilla.core.typing import ActionMiddleware
from avilla.core.utilles.selector import Selector, Summarizable

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
        current: dict[str, str] = {}
        stack = [_as_asynciter([selector])]
        for key, value in selector.pattern.items():
            if key == "land":
                continue
            depth = selector.mixin(".".join(current.keys()) + key, Selector.from_dict({**current, key: value}))  # NEED TO FIX
            for i in self.protocol.protocol_query_handlers:
                with suppress(TypeError):
                    if i.prefix.match(depth):
                        querier_type = i
                        break
            else:                
                raise ValueError(f"No query handler found for {depth.path}")
            querier = querier_type(self.protocol)
            if key not in querier.queriers:
                raise ValueError(f"No querier found for {current}, which need to apply {key}")
            async def gen(a):
                async for prefix in a:
                    print(depth, depth.pattern)
                    async for i in querier.queriers[key](querier, self, prefix, depth.match):
                        yield i
            stack.append(gen(stack[-1]))
            current = {**current, key: value}
        async for i in stack[-1]:
            yield i

    @overload
    async def meta(self, op_or_target: type[_M]) -> _M:
        ...

    @overload
    async def meta(self, op_or_target: list[Modify[_T]]) -> _T:
        ...

    @overload
    async def meta(self, op_or_target: Any, op: type[_M]) -> _M:
        ...

    @overload
    async def meta(self, op_or_target: Any, op: list[Modify]) -> _T:
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
