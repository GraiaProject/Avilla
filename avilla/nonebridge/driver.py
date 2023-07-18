from __future__ import annotations

from typing import TYPE_CHECKING, Any, Callable

from loguru import logger
from nonebot.config import Config
from nonebot.drivers._lifespan import Lifespan
from nonebot.internal.driver import Driver as BaseDriver

if TYPE_CHECKING:
    from .service import NoneBridgeService


class NoneBridgeDriver(BaseDriver):
    def __init__(self, service: NoneBridgeService):
        self.service = service
        self.lifespan_agent = Lifespan()
        self.config = Config(
            driver="avilla.nonebot.driver",
            superusers=set(),  # TODO
            nickname=set(),
        )

    @property
    def type(self) -> str:
        return "nonebridge"

    @property
    def logger(self):
        return logger

    @property
    def bots(self):
        # TODO: fetch from service/ avilla instance
        return {}

    def run(self, *args, **kwargs):
        # 这里已经由 launart 接管, 理应不会被调用.
        return super().run(*args, **kwargs)

    def on_startup(self, func: Callable[..., Any]) -> Callable[..., Any]:
        return self.lifespan_agent.on_startup(func)

    def on_shutdown(self, func: Callable[..., Any]) -> Callable[..., Any]:
        return self.lifespan_agent.on_shutdown(func)
