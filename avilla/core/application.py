from __future__ import annotations

import importlib.metadata
import re
from inspect import cleandoc
from typing import cast

from graia.broadcast import Broadcast
from launart import Launart, Service
from loguru import logger

from avilla.core.account import AbstractAccount
from avilla.core.action.extension import ActionExtension
from avilla.core.action.middleware import ActionMiddleware
from avilla.core.context import get_current_avilla
from avilla.core.dispatchers import (
    AvillaBuiltinDispatcher,
    MetadataDispatcher,
    RelationshipDispatcher,
)
from avilla.core.platform import Land
from avilla.core.protocol import BaseProtocol
from avilla.core.resource import ResourceProvider
from avilla.core.service import AvillaService
from avilla.core.typing import ActionExtensionImpl
from avilla.core.utilles.selector import Selector

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


GRAIA_PROJECT_REPOS = [
    "avilla-core",
    "graia-broadcast",
    "graia-saya",
    "graia-scheduler",
    "graia-ariadne" "statv",
    "launart",
    "creart",
    "creart-graia",
    "kayaku",
]


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
    protocols: list[BaseProtocol]
    action_middlewares: list[ActionMiddleware]
    resource_providers: dict[str, ResourceProvider]
    extension_impls: dict[type[ActionExtension], ActionExtensionImpl]
    accounts: list[AbstractAccount]
    service: AvillaService

    # NOTE: configuration is done by kayaku.
    def __init__(
        self,
        broadcast: Broadcast,
        protocols: list[BaseProtocol],
        services: list[Service],
        middlewares: list[ActionMiddleware] | None = None,
        launch_manager: Launart | None = None,
    ):
        if len({type(i) for i in protocols}) != len(protocols):
            raise ValueError("protocol must be unique, and the config should be passed by config.")

        self.broadcast = broadcast
        self.launch_manager = launch_manager or Launart()
        self.protocols = protocols
        self._protocol_map = {type(i): i for i in protocols}
        self.action_middlewares = middlewares or []
        self.accounts = []
        self.resource_providers = {}
        self.extension_impls = {}
        self.service = AvillaService(self)

        for service in services:
            self.launch_manager.add_service(service)

        self.launch_manager.add_service(self.service)

        for protocol in self.protocols:
            # Ensureable 用于注册各种东西, 包括 Service, ResourceProvider 等.
            protocol.ensure(self)

        self.broadcast.finale_dispatchers.append(MetadataDispatcher())
        self.broadcast.finale_dispatchers.append(AvillaBuiltinDispatcher(self))
        self.broadcast.finale_dispatchers.append(RelationshipDispatcher())

    @classmethod
    def current(cls) -> "Avilla":
        return get_current_avilla()

    @property
    def loop(self):
        return self.broadcast.loop

    def add_action_middleware(self, middleware: ActionMiddleware):
        self.action_middlewares.append(middleware)

    def remove_action_middleware(self, middleware: ActionMiddleware):
        self.action_middlewares.remove(middleware)

    def get_resource_provider(self, resource: Selector) -> ResourceProvider | None:
        return self.resource_providers.get(cast(str, resource.latest_key))

    def add_resource_provider(self, provider: ResourceProvider, *resource_types: str):
        for resource_type in resource_types:
            self.resource_providers[resource_type] = provider

    def remove_resource_provider(self, provider: ResourceProvider):
        for resource_type in self.resource_providers:
            if self.resource_providers[resource_type] is provider:
                del self.resource_providers[resource_type]

    def add_account(self, account: AbstractAccount):
        if account in self.accounts:
            raise ValueError("account already exists.")
        self.accounts.append(account)

    def remove_account(self, account: AbstractAccount):
        if account not in self.accounts:
            raise ValueError("account not exists.")
        self.accounts.remove(account)

    def get_account(
        self, account_id: str | None = None, selector: Selector | None = None, land: Land | None = None
    ) -> AbstractAccount | None:
        for account in self.accounts:
            if account_id is not None and account.id != account_id:
                continue
            if selector is not None and not selector.match(account.to_selector()):
                continue
            if land is not None and account.land != land:
                continue
            return account

    def get_accounts(
        self, account_id: str | None = None, selector: Selector | None = None, land: Land | None = None
    ) -> list[AbstractAccount]:
        result = []
        for account in self.accounts:
            if account_id is not None and account.id != account_id:
                continue
            if selector is not None and not selector.match(account.to_selector()):
                continue
            if land is not None and account.land != land:
                continue
            result.append(account)
        return result

    async def launch(self):
        logger.info(AVILLA_ASCII_RAW_LOGO, alt=AVILLA_ASCII_LOGO)
        _log_telemetry()

        for protocol in self.protocols:
            if protocol.__class__.platform is not BaseProtocol.platform:
                logger.info(
                    f"Using platform: {protocol.__class__.platform}",
                    alt=f"[magenta]Using platform: [/][dark_orange]{protocol.__class__.platform}[/]",
                )

        await self.launch_manager.launch()
