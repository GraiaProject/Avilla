from __future__ import annotations

from typing import TYPE_CHECKING, Any

from nonebot.adapters import Adapter as BaseAdapter

from .bot import NoneBridgeBot

if TYPE_CHECKING:
    from .service import NoneBridgeService


class NoneBridgeAdapter(BaseAdapter):
    def __init__(self, service: NoneBridgeService):
        self.service = service

    @property
    def bots(self):
        # TODO: 和 driver 的一样.
        return {}

    @classmethod
    def get_name(cls) -> str:
        # 我的目的是 mocking ob11 adapter.
        return "OneBot V11"

    @property
    def driver(self):
        return self.service.driver

    async def _call_api(self, bot: NoneBridgeBot, api: str, **data: Any):
        ...
        # TODO: Ryanvk staff.
