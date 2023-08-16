from __future__ import annotations

from typing import TYPE_CHECKING, Any

from nonebot.adapters import Adapter as BaseAdapter

from avilla.core._runtime import cx_context

from .bot import NoneBridgeBot

if TYPE_CHECKING:
    from .service import NoneBridgeService


class NoneBridgeAdapter(BaseAdapter):
    def __init__(self, service: NoneBridgeService):
        self.service = service

    @property
    def bots(self):
        return self.service.bots

    @classmethod
    def get_name(cls) -> str:
        return "OneBot V11"

    @property
    def driver(self):
        return self.service.driver

    async def _call_api(self, bot: NoneBridgeBot, api: str, **data: Any):
        staff = bot.service.staff
        maybe_cx = cx_context.get(None)
        if maybe_cx is not None:
            staff = staff.ext(maybe_cx.get_staff_components())
        else:
            staff = staff.ext(bot.account.get_staff_components())
        return staff.call_endpoint_api(api, **data)
