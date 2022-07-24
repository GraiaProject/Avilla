from __future__ import annotations

from typing import ClassVar, Literal

from launart import Launart, Service
from launart.service import Service

from avilla.onebot.v11.connection import (
    OneBot11Connection,
    OneBot11HttpClientConnection,
    OneBot11HttpServerConnection,
    OneBot11WebsocketClientConnection,
    OneBot11WebsocketServerConnection,
)
from avilla.onebot.v11.protocol import OneBot11Protocol


class OneBot11Service(Service):
    id = "onebot11.service"

    protocol: OneBot11Protocol
    connections: list[OneBot11Connection]

    def __init__(self, protocol: OneBot11Protocol) -> None:
        self.protocol = protocol
        self.connections = []

    async def launch(self, manager: Launart):
        pass

    @property
    def required(self) -> set[str]:
        required: set[str] = set()
        connection_types = {type(connection) for connection in self.connections}
        if {OneBot11HttpClientConnection, OneBot11WebsocketClientConnection} & connection_types:
            required.add("http.universal_client")
        if {OneBot11HttpServerConnection, OneBot11WebsocketServerConnection} & connection_types:
            required.add("http.universal_server")

        return required

    stages: ClassVar[set[Literal["prepare", "blocking", "cleanup"]]] = {"prepare", "blocking", "cleanup"}

    def get_interface(self, _):
        return None
