from contextlib import AsyncExitStack
from typing import TYPE_CHECKING, Any, Generic, List, TypedDict, TypeVar, Union, cast

from avilla.core.execution import Execution
from avilla.core.selectors import entity as entity_selector
from avilla.core.selectors import mainline as mainline_selector
from avilla.core.selectors import resource as resource_selector
from avilla.core.selectors import self as self_selector
from avilla.core.typing import TExecutionMiddleware

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

    def __await__(self):
        exit_stack = AsyncExitStack()
        yield from exit_stack.__aenter__().__await__()
        try:
            for middleware in self.middlewares:
                yield from exit_stack.enter_async_context(
                    middleware(self.relationship, self.execution)  # type: ignore
                ).__await__()
            result = yield from self.relationship.protocol.ensure_execution(self.execution)  # type: ignore
            return result
        finally:
            yield from exit_stack.__aexit__(None, None, None).__await__()

    def execute(self, execution: "Execution"):
        self.execution = execution
        return self

    __call__ = execute

    def to(self, target: Union[entity_selector, mainline_selector]):
        self.meta["to"] = target
        return self

    def use(self, middleware: TExecutionMiddleware):
        self.middlewares.append(middleware)
        return self


class _RelationshipMetaWrapper:
    relationship: "Relationship"

    def __init__(self, relationship: "Relationship") -> None:
        self.relationship = relationship

    async def get(self, metakey: str) -> Any:
        return await self.relationship.protocol.operate_metadata(
            self.relationship, metakey, "get", None  # type: ignore
        )

    async def set(self, metakey: str, value: Any) -> None:
        await self.relationship.protocol.operate_metadata(self.relationship, metakey, "set", value)  # type: ignore

    async def reset(self, metakey: str) -> None:
        await self.relationship.protocol.operate_metadata(self.relationship, metakey, "reset", None)  # type: ignore

    async def prev(self, metakey: str) -> Any:
        return await self.relationship.protocol.operate_metadata(
            self.relationship, metakey, "prev", None  # type: ignore
        )

    async def next(self, metakey: str) -> Any:
        return await self.relationship.protocol.operate_metadata(
            self.relationship, metakey, "next", None  # type: ignore
        )

    async def push(self, metakey: str, value: Any) -> None:
        await self.relationship.protocol.operate_metadata(self.relationship, metakey, "push", value)  # type: ignore

    async def pop(self, metakey: str, index: int) -> Any:
        return await self.relationship.protocol.operate_metadata(
            self.relationship, metakey, "pop", index  # type: ignore
        )

    async def add(self, metakey: str, value: Any) -> None:
        await self.relationship.protocol.operate_metadata(self.relationship, metakey, "add", value)  # type: ignore

    async def remove(self, metakey: str, value: Any) -> None:
        await self.relationship.protocol.operate_metadata(self.relationship, metakey, "remove", value)  # type: ignore


M = TypeVar("M", bound=_RelationshipMetaWrapper)


class Relationship(Generic[M]):
    ctx: Union[entity_selector, mainline_selector]
    mainline: mainline_selector
    self: self_selector
    via: Union[mainline_selector, entity_selector, None] = None

    protocol: "BaseProtocol"

    _middlewares: List[TExecutionMiddleware]

    def __init__(
        self,
        protocol: "BaseProtocol",
        ctx: Union[entity_selector, mainline_selector],
        mainline: mainline_selector,
        current_self: self_selector,
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
    def current(self) -> self_selector:
        return self.self or self.protocol.get_self()

    @property
    def meta(self) -> M:
        return cast(M, _RelationshipMetaWrapper(self))

    @property
    def exec(self):
        return ExecutorWrapper(self)

    def fetch(self, resource: resource_selector):
        return self.protocol.fetch_resource(resource)

    def has_ability(self, ability: str) -> bool:
        return self.protocol.has_ability(ability)


class CoreSupport(_RelationshipMetaWrapper):
    "see pyi"
    pass
