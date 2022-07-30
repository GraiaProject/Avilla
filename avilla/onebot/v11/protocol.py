from __future__ import annotations

from collections.abc import Iterable

from avilla.core.application import Avilla
from avilla.core.account import AbstractAccount
from avilla.core.platform import Abstract, Land, Platform, Version
from avilla.core.protocol import BaseProtocol
from avilla.core.utilles.selector import Selector

from .account import OneBot11Account
from .connection import (
    OneBot11Connection,
    OneBot11HttpClientConnection,
    OneBot11HttpServerConnection,
    OneBot11WebsocketClientConnection,
    OneBot11WebsocketServerConnection,
)
from .connection.config import (
    OneBot11Config,
    OneBot11HttpClientConfig,
    OneBot11HttpServerConfig,
    OneBot11WebsocketClientConfig,
    OneBot11WebsocketServerConfig,
)
from .service import OneBot11Service

_config_map: dict[type[OneBot11Config], type[OneBot11Connection]] = {
    OneBot11HttpClientConfig: OneBot11HttpClientConnection,
    OneBot11HttpServerConfig: OneBot11HttpServerConnection,
    OneBot11WebsocketClientConfig: OneBot11WebsocketClientConnection,
    OneBot11WebsocketServerConfig: OneBot11WebsocketServerConnection,
}


class OneBot11Protocol(BaseProtocol):
    platform = Platform(
        Land(
            name="onebot",
            maintainers=[{"name": "GraiaProject"}],
            humanized_name="OneBot",
        ),
        Abstract(
            protocol="onebot",
            maintainers=[{"name": "howmanybots"}],
            humanized_name="OneBot",
        ),
        Version(
            {
                "onebot_spec": "v11",
            }
        ),
    )
    message_serializer = OneBot11MessageSerializer()
    message_deserializer = OneBot11MessageDeserializer()

    completion_rules = {}

    event_parser = OneBot11EventParser()
    action_executors = [
        OneBot11GroupActionExecutor,
        OneBot11FriendActionExecutor,
        OneBot11GroupMemberActionExecutor,
    ]

    accounts: dict[str, OneBot11Account]
    configs: dict[str, Iterable[OneBot11Config]]
    service: OneBot11Service

    def __init__(self, configs: dict[str, Iterable[OneBot11Config]]) -> None:
        self.configs = configs

    def ensure(self, avilla: Avilla) -> None:
        self.avilla = avilla
        self.service = OneBot11Service(self)
        avilla.launch_manager.add_service(self.service)

        for id_, configs in self.configs.items():
            account = OneBot11Account(id_, self)
            avilla.add_account(account)
            for config in configs:
                connection = _config_map[type(config)](account, config)
                if getattr(account, connection.name) is not None:
                    raise ValueError(f"Account already has a {type(connection).__name__} connection")
                setattr(account, connection.name, connection)
                self.service.connections.append(connection)
                avilla.launch_manager.add_launchable(connection)

    def get_account(self, selector: Selector) -> OneBot11Account | AbstractAccount | None:
        return self.accounts.get(selector.pattern.get("account", "")) or super().get_account(selector)
