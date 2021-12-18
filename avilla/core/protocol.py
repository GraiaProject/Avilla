from abc import ABCMeta, abstractmethod
from contextlib import AsyncExitStack
from typing import TYPE_CHECKING, Any, ClassVar, Generic, List, Set, Tuple, Type, Union

from avilla.core.launch import LaunchComponent
from avilla.core.message import MessageChain
from avilla.core.platform import Platform
from avilla.core.selectors import mainline as mainline_selector
from avilla.core.selectors import self as self_selector
from avilla.core.typing import METADATA_VALUE, T_Config, T_ExecMW
from avilla.core.utilles.selector import Selector

from .execution import Execution

if TYPE_CHECKING:
    from avilla.core.relationship import Relationship

    from . import Avilla


class BaseProtocol(Generic[T_Config], metaclass=ABCMeta):
    avilla: "Avilla"
    config: T_Config

    platform: Platform = Platform(
        name="Avilla Universal Protocol Implementation",
        protocol_provider_name="Avilla Protocol",
        implementation="avilla-core",
        supported_impl_version="$any",
        generation="1",
    )

    required_services: ClassVar[Set[str]]

    def __init__(self, avilla: "Avilla", config: T_Config) -> None:
        self.avilla = avilla
        self.config = config
        self.using_networks, self.using_exec_method = self.ensure_networks()
        self.__post_init__()

    @abstractmethod
    def ensure_networks(self):
        raise NotImplementedError

    def __post_init__(self) -> None:
        pass

    async def ensure_execution(self, execution: "Execution") -> Any:
        raise NotImplementedError

    @abstractmethod
    def get_self(self) -> "self_selector":
        raise NotImplementedError

    @abstractmethod
    async def parse_message(self, data: Any) -> "MessageChain":
        raise NotImplementedError

    @abstractmethod
    async def serialize_message(self, message: "MessageChain") -> Any:
        raise NotImplementedError

    @abstractmethod
    async def launch_mainline(self):
        """LaunchComponent.task"""

    if TYPE_CHECKING:
        async def launch_prepare(self):
            """LaunchComponent.prepare"""

        async def launch_cleanup(self):
            """LaunchComponent.cleanup"""
    else:
        launch_prepare = None
        launch_cleanup = None

    @property
    def launch_component(self) -> LaunchComponent:
        return LaunchComponent(
            f"avilla.core.protocol:{self.platform.implementation}",
            self.required_services,
            self.launch_mainline,
            self.launch_prepare,
            self.launch_cleanup,
        )

    def has_ability(self, ability: str) -> bool:
        raise NotImplementedError

    async def exec_directly(self, execution: Execution, *middlewares: T_ExecMW) -> Any:
        async with AsyncExitStack() as exit_stack:
            for middleware in middlewares:
                await exit_stack.enter_async_context(middleware(self, execution))  # type: ignore
            return await self.ensure_execution(execution)

    def check_mainline(self, mainline: mainline_selector) -> bool:
        return True

    async def check_metadata_access(
        self, metascope: Type[Selector], metakey: str, operator: str
    ) -> Union[List[str], None]:
        return None

    @abstractmethod
    async def operate_metadata(
        self, relationship: "Relationship", metakey: str, operator: str, value: METADATA_VALUE
    ) -> Any:
        ...

    @property
    def protocol_ranks(self) -> Tuple[str, ...]:
        return ()
