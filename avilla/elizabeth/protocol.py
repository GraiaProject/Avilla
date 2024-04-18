from __future__ import annotations

from dataclasses import dataclass, field

from yarl import URL

from avilla.core.application import Avilla
from avilla.core.protocol import BaseProtocol, ProtocolConfig
from graia.ryanvk import merge, ref

from .connection.ws_client import ElizabethWsClientNetworking
from .service import ElizabethService


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
    from avilla.elizabeth.perform.action import contact  # noqa: F401
    from avilla.elizabeth.perform.action import (
        activity,
        announcement,
        file,
        friend,
        group,
        member,
        message,
        request,
    )
    from avilla.elizabeth.perform.event import activity  # noqa: F401, F811
    from avilla.elizabeth.perform.event import friend  # noqa: F811
    from avilla.elizabeth.perform.event import group  # noqa: F811
    from avilla.elizabeth.perform.event import member  # noqa: F401, F811
    from avilla.elizabeth.perform.event import message  # noqa: F401, F811
    from avilla.elizabeth.perform.event import relationship  # noqa: F401
    from avilla.elizabeth.perform.event import request  # noqa: F401, F811
    from avilla.elizabeth.perform.message import deserialize, serialize  # noqa
    from avilla.elizabeth.perform.query import announcement, bot, file, friend, group  # noqa


_import_performs()


class ElizabethProtocol(BaseProtocol):
    service: ElizabethService

    artifacts = {
        **merge(
            ref("avilla.protocol/elizabeth::action", "activity"),
            ref("avilla.protocol/elizabeth::action", "announcement"),
            ref("avilla.protocol/elizabeth::action", "contact"),
            ref("avilla.protocol/elizabeth::action", "file"),
            ref("avilla.protocol/elizabeth::action", "friend"),
            ref("avilla.protocol/elizabeth::action", "group"),
            ref("avilla.protocol/elizabeth::action", "member"),
            ref("avilla.protocol/elizabeth::action", "message"),
            ref("avilla.protocol/elizabeth::action", "request"),
            ref("avilla.protocol/elizabeth::event", "activity"),
            ref("avilla.protocol/elizabeth::event", "friend"),
            ref("avilla.protocol/elizabeth::event", "group"),
            ref("avilla.protocol/elizabeth::event", "member"),
            ref("avilla.protocol/elizabeth::event", "message"),
            ref("avilla.protocol/elizabeth::event", "relationship"),
            ref("avilla.protocol/elizabeth::event", "request"),
            ref("avilla.protocol/elizabeth::message", "deserialize"),
            ref("avilla.protocol/elizabeth::message", "serialize"),
            ref("avilla.protocol/elizabeth::query", "announcement"),
            ref("avilla.protocol/elizabeth::query", "bot"),
            ref("avilla.protocol/elizabeth::query", "file"),
            ref("avilla.protocol/elizabeth::query", "friend"),
            ref("avilla.protocol/elizabeth::query", "group"),
            ref("avilla.protocol/elizabeth::resource_fetch"),
            ref("avilla.protocol/elizabeth::context"),
        )
    }

    def __init__(self):
        self.service = ElizabethService(self)

    def ensure(self, avilla: Avilla):
        self.avilla = avilla

        avilla.launch_manager.add_component(self.service)

    def configure(self, config: ElizabethConfig):
        self.service.connections.append(ElizabethWsClientNetworking(self, config))
        return self
