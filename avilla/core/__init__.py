from __future__ import annotations

import importlib.metadata
import re
from contextlib import asynccontextmanager
from inspect import cleandoc
from typing import List, Optional

from graia.amnesia.launch.manager import LaunchManager
from graia.amnesia.launch.service import Service
from graia.broadcast import Broadcast
from graia.broadcast.entities.dispatcher import BaseDispatcher
from graia.broadcast.interfaces.dispatcher import DispatcherInterface
from loguru import logger

from avilla.core.context import get_current_avilla
from avilla.core.event import RelationshipDispatcher
from avilla.core.execution import Execution
from avilla.core.metadata.interface import MetadataInterface
from avilla.core.protocol import BaseProtocol
from avilla.core.relationship import Relationship
from avilla.core.resource.interface import ResourceInterface
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

    launch_manager: LaunchManager
    metadata_interface: MetadataInterface
    resource_interface: ResourceInterface
    protocols: List[BaseProtocol]

    exec_middlewares: List[TExecutionMiddleware]
    # TODO: Better Config using Ensureable, Status(amnesia)

    def __init__(
        self,
        broadcast: Broadcast,
        protocols: List[BaseProtocol],
        services: List[Service],
        middlewares: Optional[List[TExecutionMiddleware]] = None,
        launch_manager: Optional[LaunchManager] = None,
    ):
        if len(set(type(i) for i in protocols)) != len(protocols):
            raise ValueError("protocol must be unique, and the config should be passed by config.")

        self.broadcast = broadcast
        self.launch_manager = launch_manager or LaunchManager()
        self.metadata_interface = MetadataInterface()
        self.resource_interface = ResourceInterface()
        self.protocols = protocols
        self._protocol_map = {type(i): i for i in protocols}
        self.exec_middlewares = []
        if middlewares:
            self.exec_middlewares.extend(middlewares)
        self.launch_manager.update_services(services)
        self.launch_manager.update_launch_components([i.launch_component for i in self.launch_manager.services])

        for protocol in self.protocols:
            # Ensureable 用于注册各种东西, 包括 Service, ResourceProvider 等.
            # 相对的, 各个 Protocol 实例各维护/调用一个 Profile, 这个也算是 Config 相关的妥协
            protocol.ensure(self)

        self.broadcast.finale_dispatchers.append(RelationshipDispatcher())

        class AvillaBuiltinDispatcher(BaseDispatcher):
            @staticmethod
            async def catch(interface: DispatcherInterface):
                if interface.annotation is Avilla:
                    return self
                elif interface.annotation in self._protocol_map:
                    return self._protocol_map[interface.annotation]

        self.broadcast.finale_dispatchers.append(AvillaBuiltinDispatcher)

        @asynccontextmanager
        async def _rs_target_ensure(rs: Relationship, exec: Execution):
            if not exec.located:
                if exec.locate_type == "mainline":
                    exec.locate_target(rs.mainline)
                elif exec.locate_type == "ctx":
                    exec.locate_target(rs.ctx)
                elif exec.locate_type == "via":
                    exec.locate_target(rs.via)  # type: ignore
                elif exec.locate_type == "current":
                    exec.locate_target(rs.current)
                else:
                    logger.warning(f"unknown locate_type: {exec} - {exec.locate_type}")
            yield

        self.exec_middlewares.append(_rs_target_ensure)
        # 或者给 avilla 相关写个服务, get_interface 之类的分发功能
        # ？！
        """
        # config shortcut flatten

        self.config = {}
        for applicant, target_conf in config.items():
            if not isinstance(target_conf, dict):
                target_conf = {...: target_conf}

            for scope, shortcut in target_conf.items():
                if not isinstance(shortcut, ConfigProvider):
                    if isinstance(shortcut, BaseModel):
                        target_conf[scope] = direct(shortcut)  # type: ignore
                    else:
                        raise ValueError(f"invalid configuration: {shortcut}")

            self.config[applicant] = target_conf  # type: ignore
        self.config.setdefault(Avilla, {...: direct(AvillaConfig())})  # type: ignore
        # all use default value.

        # builtin settings
        avilla_config = cast(AvillaConfig, self.get_config(Avilla))
        if avilla_config.enable_builtin_services:
            if avilla_config.use_memcache:
                self.add_service(MemcacheService())
        if avilla_config.use_defer:
            self.broadcast.finale_dispatchers.append(DeferDispatcher())
        """

    """
    def get_config(
        self, applicant: Union[ConfigApplicant[TModel], Type[ConfigApplicant[TModel]]], scope: Hashable = ...
    ) -> Optional[TModel]:
        scoped = cast(Dict[Hashable, "ConfigProvider[TModel]"], self.config.get(applicant))
        if scoped:
            provider = scoped.get(scope)
            if provider:
                return provider.get_config()

    def get_config_scopes(self, applicant: Union[ConfigApplicant[TModel], Type[ConfigApplicant[TModel]]]):
        scoped = self.config.get(applicant)
        if scoped:
            return scoped.keys()

    async def flush_config(self, when: ConfigFlushingMoment):
        for applicant, scoped in self.config.items():
            if when not in applicant.init_moment.values():
                continue
            for scope, provider in scoped.items():
                await provider.provide(self, applicant.config_model, scope)
    """

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
