from __future__ import annotations

import py_compile
from contextlib import AsyncExitStack
from typing import TYPE_CHECKING, Any, Generic, TypeVar, cast, overload

from avilla.core.context import ctx_relationship
from avilla.core.execution import Execution
from avilla.core.metadata.model import Metadata, MetadataModifies
from avilla.core.resource import Resource
from avilla.core.selectors import entity as entity_selector
from avilla.core.selectors import mainline as mainline_selector
from avilla.core.selectors import request as request_selector
from avilla.core.typing import TExecutionMiddleware
from avilla.core.utilles.selector import Selector

if TYPE_CHECKING:
    from avilla.core.protocol import BaseProtocol


class ExecutorWrapper:
    relationship: Relationship
    execution: Execution
    middlewares: list[TExecutionMiddleware]

    def __init__(self, relationship: Relationship) -> None:
        self.relationship = relationship
        self.middlewares = relationship.protocol.avilla.exec_middlewares.copy()

    def __await__(self):
        return self.ensure().__await__()

    async def ensure(self):
        async with AsyncExitStack() as stack:
            for middleware in reversed(self.middlewares):
                await stack.enter_async_context(middleware(self.relationship, self.execution))
            return await self.relationship.protocol.ensure_execution(self.execution)

    def execute(self, execution: Execution):
        self.execution = execution
        return self

    __call__ = execute

    def to(self, target: entity_selector | mainline_selector):
        self.execution.locate_target(target)
        return self

    def use(self, middleware: TExecutionMiddleware):
        self.middlewares.append(middleware)
        return self


class RelationshipQueryWarpper:
    relationship: Relationship
    pattern: ...  # TODO: Selector Query Pattern

    async def __aiter__(self):
        ...


M = TypeVar("M", entity_selector, mainline_selector, request_selector, Selector)

_T = TypeVar("_T")
_M = TypeVar("_M", bound=Metadata)


class Relationship(Generic[M]):
    ctx: M
    mainline: mainline_selector
    current: entity_selector
    via: entity_selector | mainline_selector | None

    protocol: "BaseProtocol"

    _middlewares: list[TExecutionMiddleware]

    def __init__(
        self,
        protocol: "BaseProtocol",
        ctx: M,
        mainline: mainline_selector,
        current: entity_selector,
        via: mainline_selector | entity_selector | None = None,
        middlewares: list[TExecutionMiddleware] | None = None,
    ) -> None:
        self.ctx = ctx
        self.mainline = mainline
        self.via = via
        self.current = current
        self.protocol = protocol
        self._middlewares = middlewares or []

    @property
    def exec(self):
        return ExecutorWrapper(self)

    @property
    def avilla(self):
        return self.protocol.avilla

    @overload
    async def complete(self, selector: mainline_selector) -> mainline_selector:
        ...

    @overload
    async def complete(self, selector: entity_selector) -> entity_selector:
        ...

    async def complete(self, selector: ...) -> ...:
        if isinstance(selector, mainline_selector):
            tempdict = self.mainline.path.copy()
            tempdict.update(selector.path)
            return self.protocol.complete_selector(mainline_selector(tempdict))
        elif isinstance(selector, entity_selector):
            if "mainline" not in selector.path:
                selector.path["mainline"] = self.mainline
            return self.protocol.complete_selector(selector)
        else:
            raise TypeError(f"{selector} is not a supported selector for rs.complete.")

    async def fetch(self, resource: Resource[_T]) -> _T:
        with ctx_relationship.use(self):  # 可能在 provider 内部引用的组件有要用到的.
            provider = self.avilla.resource_interface.get_provider(resource)
            if not provider:
                raise ValueError(f"{type(resource)} is not a supported resource.")
            return await provider.fetch(resource, self)

    async def query(self, pattern: ...) -> RelationshipQueryWarpper:
        ...
        # TODO: rs.query to query entities in mainline, which match the pattern.

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
                (op_or_target, None if op is None else op_or_target, op),
            )

            if isinstance(op, type) and issubclass(op, Metadata):
                modify = None
                model = op
            elif isinstance(op, MetadataModifies):
                modify = op
                model = op.model
            else:
                raise TypeError(f"{op_or_target} & {op} is not a supported metadata operation for rs.meta.")

            target = target or model.default_target_by_relationship(cast(Relationship[Selector], self))

            if target is None:
                if modify is None:
                    raise ValueError(
                        f"{model} is not a supported metadata for rs.meta, which requires a categorical target."
                    )
                raise ValueError(
                    f"{model}'s modify is not a supported metadata for rs.meta, which requires a categorical target."
                )

            source = self.avilla.metadata_interface.get_source(target, model)

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
