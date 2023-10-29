from __future__ import annotations

import asyncio
import json
from contextlib import suppress
from typing import TYPE_CHECKING, Any, ClassVar

import nonebot
from graia.broadcast.utilles import run_always_await
from launart import Launart, Service, any_completed
from loguru import logger
from nonebot.message import handle_event

from avilla.core.account import BaseAccount
from avilla.core.event import AvillaEvent
from avilla.core.ryanvk.staff import Staff
from avilla.core.utilles import identity
from avilla.standard.core.account import AccountRegistered, AccountUnregistered
from graia.ryanvk import merge, ref
from graia.ryanvk.aio import queue_task

from .adapter import NoneBridgeAdapter
from .bot import NoneBridgeBot
from .dispatcher import AllEventQueue
from .driver import NoneBridgeDriver

if TYPE_CHECKING:
    from avilla.core import Avilla


class NoneBridgeService(Service):
    id = "nonebridge.service"
    required: set[str] = set()
    stages: set[str] = {"preparing", "blocking", "cleanup"}

    avilla: Avilla

    driver: NoneBridgeDriver
    adapter: NoneBridgeAdapter
    staff: Staff
    bots: dict[str, NoneBridgeBot]  # key 是 Selector.pattern 的 json
    queuer: AllEventQueue[AvillaEvent]

    artifacts: ClassVar[dict[Any, Any]] = {
        **ref("avilla.protocol/onebot_v11::message", "serialize"),
        **ref("avilla.protocol/onebot_v11::message", "deserialize"),
    }

    def __init__(self, avilla: Avilla) -> None:
        super().__init__()
        self.avilla = avilla
        self.driver = NoneBridgeDriver(self)
        self.adapter = NoneBridgeAdapter(self)
        self.staff = Staff([self.artifacts], {"avilla": avilla, "nonebridge.service": self})
        self.bots = {}
        self.queuer = AllEventQueue()

        avilla.broadcast.receiver(AccountRegistered)(self.on_account_registered)
        avilla.broadcast.receiver(AccountUnregistered)(self.on_account_unregistered)
        avilla.broadcast.prelude_dispatchers.append(self.queuer)

        self._init_nonebot()

    def _init_nonebot(self):
        self.driver._adapters[self.adapter.get_name()] = self.adapter
        nonebot._driver = self.driver

    async def on_account_registered(self, event: AccountRegistered):
        key = json.dumps({**event.account.route.pattern})
        self.bots[key] = NoneBridgeBot(self, event.account)

    async def on_account_unregistered(self, event: AccountUnregistered):
        key = json.dumps({**event.account.route.pattern})
        if key not in self.bots:
            logger.warning(f"nonebridge cannot unregister account {event.account.route}")
        del self.bots[key]

    on_account_registered.__annotations__ = {"event": AccountRegistered}
    on_account_unregistered.__annotations__ = {"event": AccountUnregistered}

    def get_mapped_bot(self, account: BaseAccount) -> NoneBridgeBot:
        return self.bots[json.dumps({**account.route.pattern})]

    async def event_translater(self):
        assert self.manager is not None

        while not self.manager.status.exiting:
            event = None

            with suppress(asyncio.TimeoutError):
                event = await asyncio.wait_for(self.queuer.queue.get(), timeout=5)

            if event is None:
                continue

            translated_event = await self.staff.translate_event(event)
            if translated_event is None:
                logger.warning(f"{identity(event)} cannot translate to nonebot event!")
                continue

            cx = event.context
            bot = self.get_mapped_bot(cx.account)

            queue_task(handle_event(bot, translated_event))

    async def launch(self, manager: Launart):
        async with self.stage("preparing"):
            # 这部分实现 nonebot.init 的部分, 同时也会对 nonebot 模块进行 bootstrap dirty hacking.
            # 目标是对 nonebot.adapters.onebot.v11 的完全运行时 hack.
            for i in self.driver.lifespan_agent._startup_funcs:
                await run_always_await(i)

        async with self.stage("blocking"):
            await any_completed(manager.status.wait_for_sigexit(), self.event_translater())

        async with self.stage("cleanup"):
            for i in self.driver.lifespan_agent._shutdown_funcs:
                await run_always_await(i)


def _import_ryanvk_performs():
    """
    # isort: off

    # 这部分会造成干扰

    token = processing_artifact_heap.set(NoneBridgeService.artifacts["ob_message_deserde"])
    from avilla.onebot.v11.perform.message.deserialize import OneBot11MessageDeserializePerform  # noqa

    processing_artifact_heap.reset(token)

    token = processing_artifact_heap.set(NoneBridgeService.artifacts["ob_message_serde"])
    from avilla.onebot.v11.perform.message.serialize import OneBot11MessageSerializePerform  # noqa

    processing_artifact_heap.reset(token)

    from .perform.event.message import MessageEventTranslater

    MessageEventTranslater.apply_to(NoneBridgeService.artifacts)
    """


_import_ryanvk_performs()
