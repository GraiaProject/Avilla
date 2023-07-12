from __future__ import annotations

from collections import ChainMap
from typing import TYPE_CHECKING, Any, Awaitable, Callable, TypeVar

import aiohttp
from loguru import logger
from typing_extensions import Concatenate

from avilla.core.application import Avilla
from avilla.core.elements import Element
from avilla.core.protocol import BaseProtocol
from avilla.core.ryanvk.descriptor.fetch import FetchImplement
from avilla.core.ryanvk.descriptor.message.deserialize import MessageDeserializeSign
from avilla.core.ryanvk.descriptor.message.serialize import MessageSerializeSign
from avilla.core.ryanvk.runner import run_fn, use_record
from graia.amnesia.message import MessageChain

from ...core.ryanvk.descriptor.event import EventParserSign
from .service import OneBot11Service

if TYPE_CHECKING:
    from avilla.core.event import AvillaEvent
    from avilla.core.resource import Resource
    from avilla.core.ryanvk.collector.account import AccountCollector

    from .account import OneBot11Account
    from .collector.connection import ConnectionCollector
    from .net.ws_client import OneBot11WsClientNetworking
    from .resource import OneBot11Resource

T = TypeVar("T")


class OneBot11Protocol(BaseProtocol):
    service: OneBot11Service

    def __init__(self):
        self.service = OneBot11Service(self)

    @classmethod
    def __init_isolate__(cls):  # ruff: noqa: F401
        # isort: off

        # :: Message
        from .perform.message.deserialize import OneBot11MessageDeserializePerform
        from .perform.message.serialize import OneBot11MessageSerializePerform

        # :: Action
        from .perform.action.message import OneBot11MessageActionPerform

        # :: Event
        from .perform.event.message import OneBot11EventMessagePerform
        from .perform.event.lifespan import OneBot11EventLifespanPerform

        # :: Resource Fetch
        from .perform.resource_fetch import OneBot11ResourceFetchPerform

    def ensure(self, avilla: Avilla):
        self.avilla = avilla

        avilla.launch_manager.add_component(self.service)

    def get_staff_components(self):
        return {"protocol": self, "avilla": self.avilla}

    def get_staff_artifacts(self):
        return ChainMap(self.isolate.artifacts, self.avilla.isolate.artifacts)