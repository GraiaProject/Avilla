from __future__ import annotations

import importlib.metadata
import re
from inspect import cleandoc

from graia.broadcast import Broadcast
from launart import Launart, Service
from loguru import logger

from avilla.core.builtins import AvillaBuiltinDispatcher, execute_target_ensure
from avilla.core.context import get_current_avilla
from avilla.core.event import RelationshipDispatcher
from avilla.core.metadata.interface import MetadataInterface
from avilla.core.protocol import BaseProtocol
from avilla.core.resource.interface import ResourceInterface
from avilla.core.resource.local import LocalFileResource, LocalFileResourceProvider
from avilla.core.typing import TExecutionMiddleware

AVILLA_ASCII_LOGO = cleandoc(
    r"""
    [bold]Avilla[/]: a universal asynchronous message flow solution, powered by [blue]Graia Project[/].
        _        _ _ _
       / \__   _(_) | | __ _
      / _ \ \ / / | | |/ _` |
     / ___ \ V /| | | | (_| |
    /_/   \_\_/ |_|_|_|\__,_|
    """
)
AVILLA_ASCII_RAW_LOGO = re.sub(r"\[.*?\]", "", AVILLA_ASCII_LOGO)


GRAIA_PROJECT_REPOS = ["avilla-core", "graia-broadcast", "graia-saya", "graia-scheduler"]


def _log_telemetry():
    for telemetry in GRAIA_PROJECT_REPOS:
        try:
            version = importlib.metadata.version(telemetry)
        except Exception:
            version = "unknown / not-installed"
        logger.info(
            f"{telemetry} version: {version}",
            alt=f"[b cornflower_blue]{telemetry}[/] version: [cyan3]{version}[/]",
        )


class Avilla:
    broadcast: Broadcast

    launch_manager: Launart
    metadata_interface: MetadataInterface
    resource_interface: ResourceInterface
    protocols: list[BaseProtocol]

    exec_middlewares: list[TExecutionMiddleware]
    # TODO: Better Config using Ensureable, Status(amnesia)

    def __init__(
        self,
        broadcast: Broadcast,
        protocols: list[BaseProtocol],
        services: list[Service],
        middlewares: list[TExecutionMiddleware] | None = None,
        launch_manager: Launart | None = None,
    ):
        if len({type(i) for i in protocols}) != len(protocols):
            raise ValueError("protocol must be unique, and the config should be passed by config.")

        self.broadcast = broadcast
        self.launch_manager = launch_manager or Launart()
        self.metadata_interface = MetadataInterface()
        self.resource_interface = ResourceInterface()
        self.protocols = protocols
        self._protocol_map = {type(i): i for i in protocols}
        self.exec_middlewares = middlewares or []

        for service in services:
            self.launch_manager.add_service(service)

        for protocol in self.protocols:
            # Ensureable 用于注册各种东西, 包括 Service, ResourceProvider 等.
            # 相对的, 各个 Protocol 实例各维护/调用一个 Profile, 这个也算是 Config 相关的妥协
            protocol.ensure(self)

        # TODO: Avilla Backend Service: 维护一些东西, 我还得再捋捋..

        self.resource_interface.register(
            LocalFileResourceProvider(), resource=lambda x: isinstance(x, LocalFileResource)
        )

        self.broadcast.finale_dispatchers.append(AvillaBuiltinDispatcher(self))
        self.broadcast.finale_dispatchers.append(RelationshipDispatcher())

        self.exec_middlewares.append(execute_target_ensure)

    @classmethod
    def current(cls) -> "Avilla":
        return get_current_avilla()

    @property
    def loop(self):
        return self.broadcast.loop

    async def launch(self):
        logger.info(AVILLA_ASCII_RAW_LOGO, alt=AVILLA_ASCII_LOGO)
        _log_telemetry()

        for protocol in self.protocols:
            if protocol.__class__.platform is not BaseProtocol.platform:
                logger.info(f"using platform: {protocol.__class__.platform}")

        await self.launch_manager.launch()
