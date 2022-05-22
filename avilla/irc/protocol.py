from __future__ import annotations

from typing import Any, ClassVar
from avilla.irc.service import IrcConnectionService

from graia.amnesia.message import MessageChain

from avilla.core import Avilla
from avilla.core.execution import Execution
from avilla.core.platform import Base, Platform
from avilla.core.protocol import BaseProtocol
from avilla.core.relationship import Relationship
from avilla.core.selectors import entity as entity_selector
from avilla.core.utilles.selector import Selector
from graia.amnesia.message.element import Text

from loguru import logger

class IrcProtocol(BaseProtocol):
    nickname: str
    servers: list[_IrcServer]

    platform_base: ClassVar[Base] = Base("GraiaProject@github", "irc", "IRC")
    platform: ClassVar[Platform] = Platform(platform_base)

    def __init__(self, nickname: str, servers: list[_IrcServer]) -> None:
        self.nickname = nickname
        self.servers = servers

    def ensure(self, avilla: Avilla) -> Any:
        if not avilla.launch_manager.has_service(IrcConnectionService):
            service = IrcConnectionService()
            avilla.launch_manager.add_service(service)
            avilla.launch_manager.update_launch_components([service.launch_component])
        else:
            service: IrcConnectionService = avilla.launch_manager.get_service(IrcConnectionService)  # type: ignore
        
        if self.nickname in service.connections:
            raise ValueError("Nickname is already set.")
        
        protocol = _IrcProtocol(self.servers, self.nickname)
        service.connections[self.nickname] = protocol


    async def ensure_execution(self, execution: Execution) -> Any:
        pass

    async def parse_message(self, data: Any) -> "MessageChain":
        assert isinstance(data, str)
        return MessageChain([Text(data)])
    
    async def serialize_message(self, message: "MessageChain") -> Any:
        if not message.only(Text):
            raise ValueError("MessageChain must only contains Text")
        return message.__str__()
    
    async def get_relationship(self, ctx: Selector, current_self: entity_selector) -> "Relationship":
        ...
