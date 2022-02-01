from contextlib import AsyncExitStack
from functools import cached_property
from typing import TYPE_CHECKING, Any, Generic, List, TypedDict, TypeVar, Union, cast

from avilla.core.execution import Execution
from avilla.core.operator import (
    MetadataOperator,
    OperatorCachePatcher,
    OperatorKeyDispatch,
)
from avilla.core.selectors import entity as entity_selector
from avilla.core.selectors import mainline as mainline_selector
from avilla.core.selectors import request as request_selector
from avilla.core.selectors import resource as resource_selector
from avilla.core.typing import TExecutionMiddleware
from avilla.core.utilles import Defer
from avilla.io.common.storage import CacheStorage

if TYPE_CHECKING:
    from avilla.core.protocol import BaseProtocol


class ExecuteMeta(TypedDict):
    to: Union[mainline_selector, entity_selector]


class ExecutorWrapper:
    relationship: "Relationship"
    execution: "Execution"
    middlewares: List[TExecutionMiddleware]

    meta: ExecuteMeta

    def __init__(self, relationship: "Relationship") -> None:
        self.relationship = relationship
        self.middlewares = []

    def __await__(self):
        return self.ensure().__await__()

    async def ensure(self):
        return await self.relationship.protocol.ensure_execution(self.execution)

    def execute(self, execution: "Execution"):
        self.execution = execution
        return self

    __call__ = execute

    def to(self, target: Union[entity_selector, mainline_selector]):
        self.execution.locate_target(target)
        return self

    def use(self, middleware: TExecutionMiddleware):
        self.middlewares.append(middleware)
        return self


M = TypeVar("M", bound=MetadataOperator)


class Relationship(Generic[M]):
    ctx: Union[entity_selector, mainline_selector, request_selector]
    mainline: mainline_selector
    self: entity_selector
    via: Union[mainline_selector, entity_selector, None] = None

    protocol: "BaseProtocol"

    _middlewares: List[TExecutionMiddleware]

    def __init__(
        self,
        protocol: "BaseProtocol",
        ctx: Union[entity_selector, mainline_selector],
        mainline: mainline_selector,
        current_self: entity_selector,
        via: Union[mainline_selector, entity_selector, None] = None,
        middlewares: List[TExecutionMiddleware] = None,
    ) -> None:
        self.ctx = ctx
        self.mainline = mainline
        self.via = via
        self.self = current_self
        self.protocol = protocol
        self._middlewares = middlewares or []

    @property
    def current(self) -> entity_selector:
        return self.self

    @cached_property
    def meta(self) -> M:
        cache = self.protocol.avilla.get_interface(CacheStorage)
        operator = OperatorKeyDispatch(
            {
                "mainline.*": self.protocol.get_operator(self.self, self.mainline),
                "self.*": self.protocol.get_operator(self.self, self.current),
                **self.protocol.get_extra_operators(self),  # type: ignore
            }
        )
        patched = OperatorCachePatcher(operator, cache)
        defer = Defer.current()
        defer.add(patched.cache.clear)
        if isinstance(self.ctx, entity_selector) and self.ctx.get_entity_type() == "member":
            operator.patterns["member.*"] = self.protocol.get_operator(self.self, self.ctx)

        elif isinstance(self.ctx, request_selector):
            operator.patterns["request.*"] = self.protocol.get_operator(self.self, self.ctx)
        elif isinstance(self.ctx, entity_selector) and self.ctx.get_entity_type() != "member":
            operator.patterns["contact.*"] = self.protocol.get_operator(self.self, self.ctx)
        return cast(M, patched)

    @property
    def exec(self):
        return ExecutorWrapper(self)

    def fetch(self, resource: resource_selector):
        return self.protocol.fetch_resource(resource)

    def has_ability(self, ability: str) -> bool:
        return self.protocol.has_ability(ability)


class CoreSupport(MetadataOperator):
    "see pyi"
    pass
