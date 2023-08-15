from __future__ import annotations

from typing import TYPE_CHECKING, Any, ClassVar

from launart import Launart, Service

from .adapter import NoneBridgeAdapter
from .driver import NoneBridgeDriver

if TYPE_CHECKING:
    from avilla.core import Avilla


class NoneBridgeService(Service):
    id = "onebot11.service"
    required: set[str] = set()
    stages: set[str] = {"preparing", "blocking", "cleanup"}

    avilla: Avilla

    driver: NoneBridgeDriver
    adapter: NoneBridgeAdapter

    artifacts: ClassVar[dict[Any, Any]] = {}

    def __init__(self, avilla: Avilla) -> None:
        self.avilla = avilla
        self.driver = NoneBridgeDriver(self)
        self.adapter = NoneBridgeAdapter(self)

    async def launch(self, manager: Launart):
        async with self.stage("preparing"):
            # 这部分实现 nonebot.init 的部分, 同时也会对 nonebot 模块进行 bootstrap dirty hacking.
            ...

        async with self.stage("blocking"):
            ...

        async with self.stage("cleanup"):
            ...


def _import_ryanvk_performs():
    # isort: off

    from avilla.onebot.v11.perform.message.deserialize import OneBot11MessageDeserializePerform  # noqa: F401

    OneBot11MessageDeserializePerform.apply_to(NoneBridgeService.artifacts)
