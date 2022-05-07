from abc import ABCMeta, abstractmethod
from contextlib import AsyncExitStack
from typing import (
    TYPE_CHECKING,
    Any,
    ClassVar,
    Dict,
    Final,
    Generic,
    List,
    Set,
    Tuple,
    Type,
    TypeVar,
    Union,
)
from avilla.core.metadata.model import MetadataModifies
from avilla.core.resource import Resource

from graia.broadcast import Dispatchable
from pydantic import BaseModel

from avilla.core.config import ConfigApplicant, ConfigFlushingMoment, TModel
from graia.amnesia.launch.component import LaunchComponent
from graia.amnesia.message import MessageChain
from avilla.core.platform import Platform
from avilla.core.selectors import entity as entity_selector
from avilla.core.selectors import mainline as mainline_selector
from avilla.core.selectors import request as request_selector
from avilla.core.stream import Stream
from avilla.core.typing import TExecutionMiddleware
from avilla.core.utilles.selector import Selector

from .execution import Execution

if TYPE_CHECKING:
    from avilla.core.relationship import Relationship

    from . import Avilla


class BaseProtocol(ConfigApplicant[TModel], metaclass=ABCMeta):
    avilla: "Avilla"
    init_moment: Final[Dict[Type[TModel], ConfigFlushingMoment]] = {}
    config_model: Type[TModel]

    platform: Platform = Platform()

    required_components: ClassVar[Set[str]]

    def __init__(self, avilla: "Avilla") -> None:
        self.avilla = avilla
        self.__post_init__()

    def __post_init__(self) -> None:
        pass

    @abstractmethod
    async def ensure_execution(self, execution: "Execution") -> Any:
        raise NotImplementedError

    @abstractmethod
    async def parse_message(self, data: Any) -> "MessageChain":
        raise NotImplementedError

    @abstractmethod
    async def serialize_message(self, message: "MessageChain") -> Any:
        raise NotImplementedError

    @abstractmethod
    async def parse_event(self, data: Any) -> Dispatchable:
        raise NotImplementedError

    @abstractmethod
    async def get_relationship(self, ctx: Selector, current_self: entity_selector) -> "Relationship":
        raise NotImplementedError

    async def exec_directly(self, execution: Execution, *middlewares: TExecutionMiddleware) -> Any:
        async with AsyncExitStack() as exit_stack:
            for middleware in middlewares:
                await exit_stack.enter_async_context(middleware(self, execution))  # type: ignore
            return await self.ensure_execution(execution)

    def complete_selector(self, selector: Selector) -> Selector:
        return selector

    async def accept_request(self, request: request_selector):
        raise NotImplementedError

    async def reject_request(self, request: request_selector):
        raise NotImplementedError

    async def ignore_request(self, request: request_selector):
        raise NotImplementedError

    async def permission_change_callback(
        self, ctx: Union[entity_selector, mainline_selector], op: str, value: str
    ) -> None:
        ...
        # TODO: 定一下各种, 比如说 op, 这里是权限系统的饼, 还没画完...
