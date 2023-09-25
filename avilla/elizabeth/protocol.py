from __future__ import annotations

from dataclasses import dataclass, field
from os.path import dirname
import pkgutil

from yarl import URL

from avilla.core.application import Avilla
from avilla.core.protocol import BaseProtocol, ProtocolConfig

from .connection.ws_client import ElizabethWsClientNetworking
from .service import ElizabethService
from graia.ryanvk import ref, merge


@dataclass
class ElizabethConfig(ProtocolConfig):
    qq: int
    host: str
    port: int
    access_token: str
    base_url: URL = field(init=False)

    def __post_init__(self):
        self.base_url = URL.build(scheme="http", host=self.host, port=self.port)


def _import_performs():  # noqa: F401

    from avilla.elizabeth.perform import context, resource_fetch  # noqa: F401
    from avilla.elizabeth.perform.action import (
        activity,
        announcement,
        contact,  # noqa: F401
        friend,
        group,
        group_member,
        message,
        request,
    )
    from avilla.elizabeth.perform.event import (
        activity,  # noqa: F401, F811
        friend,  # noqa: F811
        group,  # noqa: F811
        group_member,  # noqa: F401, F811
        message,  # noqa: F401, F811
        relationship,  # noqa: F401
        request,  # noqa: F401, F811
    )
    from avilla.elizabeth.perform.message import deserialize, serialize  # noqa
    from avilla.elizabeth.perform.query import announcement, bot, friend, group  # noqa


class ElizabethProtocol(BaseProtocol):
    service: ElizabethService

    artifacts = {
        **ref("avilla.protocol/elizabeth::action"),
        **ref("avilla.protocol/elizabeth::event"),
        **ref("avilla.protocol/elizabeth::message"),
        **ref("avilla.protocol/elizabeth::query"),
        **ref("avilla.protocol/elizabeth::resource_fetch")
    }

    def __init__(self):
        self.service = ElizabethService(self)

    def ensure(self, avilla: Avilla):
        self.avilla = avilla

        avilla.launch_manager.add_component(self.service)

    def configure(self, config: ElizabethConfig):
        self.service.connections.append(ElizabethWsClientNetworking(self, config))
        return self
