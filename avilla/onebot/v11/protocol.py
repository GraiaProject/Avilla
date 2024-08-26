from __future__ import annotations

from dataclasses import dataclass

from yarl import URL

from avilla.core.application import Avilla
from avilla.core.protocol import BaseProtocol
from graia.ryanvk import merge, ref

from .net.ws_client import OneBot11WsClientNetworking
from .net.ws_server import OneBot11WsServerNetworking
from .service import OneBot11Service


@dataclass
class OneBot11ForwardConfig:
    endpoint: URL
    access_token: str | None = None


@dataclass
class OneBot11ReverseConfig:
    prefix: str = "/"
    path: str = "onebot/v11"
    endpoint: str = "ws/universal"
    access_token: str | None = None


def _import_performs():
    from avilla.onebot.v11.perform import context, resource_fetch  # noqa: F401
    from avilla.onebot.v11.perform.action import file  # noqa: F401
    from avilla.onebot.v11.perform.action import admin  # noqa: F401
    from avilla.onebot.v11.perform.action import scene  # noqa: F401
    from avilla.onebot.v11.perform.action import message  # noqa: F401
    from avilla.onebot.v11.perform.action import mute  # noqa: F401
    from avilla.onebot.v11.perform.action import request  # noqa: F401
    from avilla.onebot.v11.perform.event import lifespan  # noqa: F401
    from avilla.onebot.v11.perform.event import message  # noqa: F401, F811
    from avilla.onebot.v11.perform.event import notice  # noqa: F401
    from avilla.onebot.v11.perform.event import request  # noqa: F401
    from avilla.onebot.v11.perform.message import deserialize  # noqa: F401
    from avilla.onebot.v11.perform.message import serialize  # noqa: F401
    from avilla.onebot.v11.perform.query import group  # noqa: F401
    from avilla.onebot.v11.perform.query import file  # noqa: F401


_import_performs()


class OneBot11Protocol(BaseProtocol):
    service: OneBot11Service

    artifacts = {
        **merge(
            ref("avilla.protocol/onebot11::context"),
            ref("avilla.protocol/onebot11::resource_fetch"),
            ref("avilla.protocol/onebot11::action", "file"),
            ref("avilla.protocol/onebot11::action", "admin"),
            ref("avilla.protocol/onebot11::action", "scene"),
            ref("avilla.protocol/onebot11::action", "message"),
            ref("avilla.protocol/onebot11::action", "mute"),
            ref("avilla.protocol/onebot11::action", "request"),
            ref("avilla.protocol/onebot11::event", "message"),
            ref("avilla.protocol/onebot11::event", "lifespan"),
            ref("avilla.protocol/onebot11::event", "notice"),
            ref("avilla.protocol/onebot11::event", "request"),
            ref("avilla.protocol/onebot11::message", "deserialize"),
            ref("avilla.protocol/onebot11::message", "serialize"),
            ref("avilla.protocol/onebot11::query", "file"),
            ref("avilla.protocol/onebot11::query", "group"),
        ),
    }

    def __init__(self):
        self.service = OneBot11Service(self)

    def ensure(self, avilla: Avilla):
        self.avilla = avilla

        avilla.launch_manager.add_component(self.service)

    def configure(self, config: OneBot11ForwardConfig | OneBot11ReverseConfig):
        if isinstance(config, OneBot11ForwardConfig):
            self.service.connections.append(OneBot11WsClientNetworking(self, config))
        elif isinstance(config, OneBot11ReverseConfig):
            self.service.connections.append(OneBot11WsServerNetworking(self, config))
        else:
            raise TypeError("Invalid config type")
        return self
