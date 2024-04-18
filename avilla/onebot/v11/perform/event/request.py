from __future__ import annotations

from datetime import datetime

from loguru import logger

from avilla.core.context import Context
from avilla.core.request import Request
from avilla.core.selector import Selector
from avilla.onebot.v11.capability import OneBot11Capability
from avilla.onebot.v11.collector.connection import ConnectionCollector
from avilla.standard.core.request import RequestEvent


class OneBot11EventRequestPerform((m := ConnectionCollector())._):
    m.namespace = "avilla.protocol/onebot11::event"
    m.identify = "request"

    @m.entity(OneBot11Capability.event_callback, raw_event="request.friend")
    async def friend(self, raw_event: dict):
        self_id = raw_event["self_id"]
        account = self.connection.accounts.get(self_id)
        if account is None:
            logger.warning(f"Unknown account {self_id} received message {raw_event}")
            return
        request = Request(
            raw_event["flag"],
            account.info.platform.land,
            Selector().land("qq").user(str(raw_event["user_id"])),
            Selector().land("qq").user(str(raw_event["user_id"])),
            account,
            datetime.fromtimestamp(raw_event["time"]),
            request_type="onebot11::friend",
            message=raw_event.get("comment"),
        )
        return RequestEvent(
            Context(
                account,
                request.sender,
                account.route,
                request.scene,
                account.route,
            ),
            request,
        )

    @m.entity(OneBot11Capability.event_callback, raw_event="request.group.add")
    @m.entity(OneBot11Capability.event_callback, raw_event="request.group.invite")
    async def group(self, raw_event: dict):
        self_id = raw_event["self_id"]
        account = self.connection.accounts.get(self_id)
        if account is None:
            logger.warning(f"Unknown account {self_id} received message {raw_event}")
            return
        request = Request(
            f'{raw_event["sub_type"]}_{raw_event["flag"]}',
            account.info.platform.land,
            Selector().land("qq").group(str(raw_event["group_id"])),
            Selector().land("qq").user(str(raw_event["user_id"])),
            account,
            datetime.fromtimestamp(raw_event["time"]),
            request_type=f"onebot11::group.{raw_event['sub_type']}",
            message=raw_event.get("comment"),
        )
        return RequestEvent(
            Context(
                account,
                request.sender,
                request.sender,
                request.scene,
                account.route,
            ),
            request,
        )
