from __future__ import annotations

from typing import TYPE_CHECKING

from avilla.core.ryanvk.collector.account import AccountCollector
from avilla.core.selector import Selector
from avilla.standard.core.request import RequestCapability

if TYPE_CHECKING:
    from ...account import ElizabethAccount  # noqa
    from ...protocol import ElizabethProtocol  # noqa


class ElizabethRequestActionPerform((m := AccountCollector["ElizabethProtocol", "ElizabethAccount"]())._):
    m.namespace = "avilla.protocol/elizabeth::action"
    m.identify = "request"

    @m.entity(RequestCapability.accept, target="land.group.request")
    async def accept_member_request(self, target: Selector) -> None:
        request_id = target.pattern["request"].split("@")[-1]
        event_id, from_id = request_id.split("/")
        await self.account.connection.call(
            "update",
            "resp_memberJoinRequestEvent",
            {
                "eventId": int(event_id),
                "fromId": int(from_id),
                "groupId": int(target.pattern["group"]),
                "operate": 0,
                "message": "",
            },
        )

    @m.entity(RequestCapability.reject, target="land.group.request")
    async def reject_member_request(self, target: Selector, reason: str | None = None, forever: bool = False) -> None:
        request_id = target.pattern["request"].split("@")[-1]
        event_id, from_id = request_id.split("/")
        await self.account.connection.call(
            "update",
            "resp_memberJoinRequestEvent",
            {
                "eventId": int(event_id),
                "fromId": int(from_id),
                "groupId": int(target.pattern["group"]),
                "operate": 3 if forever else 1,
                "message": reason or "",
            },
        )

    @m.entity(RequestCapability.ignore, target="land.group.request")
    async def ignore_member_request(self, target: Selector) -> None:
        request_id = target.pattern["request"].split("@")[-1]
        event_id, from_id = request_id.split("/")
        await self.account.connection.call(
            "update",
            "resp_memberJoinRequestEvent",
            {
                "eventId": int(event_id),
                "fromId": int(from_id),
                "groupId": int(target.pattern["group"]),
                "operate": 2,
                "message": "",
            },
        )

    @m.entity(RequestCapability.accept, target="land.group.contact.request")
    async def accept_contact_request(self, target: Selector) -> None:
        await self.account.connection.call(
            "update",
            "resp_newFriendRequestEvent",
            {
                "eventId": int(target.pattern["request"].split("@")[-1]),
                "fromId": int(target.pattern["contact"]),
                "groupId": int(target.pattern["group"]),
                "operate": 0,
                "message": "",
            },
        )

    @m.entity(RequestCapability.reject, target="land.group.contact.request")
    async def reject_contact_request(self, target: Selector, reason: str | None = None, forever: bool = False) -> None:
        await self.account.connection.call(
            "update",
            "resp_newFriendRequestEvent",
            {
                "eventId": int(target.pattern["request"].split("@")[-1]),
                "fromId": int(target.pattern["contact"]),
                "groupId": int(target.pattern["group"]),
                "operate": 2 if forever else 1,
                "message": reason or "",
            },
        )

    @m.entity(RequestCapability.accept, target="land.group.member.request")
    async def accept_bot_invited_request(self, target: Selector) -> None:
        await self.account.connection.call(
            "update",
            "resp_botInvitedJoinGroupRequestEvent",
            {
                "eventId": int(target.pattern["request"].split("@")[-1]),
                "fromId": int(target.pattern["member"]),
                "groupId": int(target.pattern["group"]),
                "operate": 0,
                "message": "",
            },
        )

    @m.entity(RequestCapability.reject, target="land.group.member.request")
    async def reject_bot_invited_request(
        self, target: Selector, reason: str | None = None, forever: bool = False
    ) -> None:
        await self.account.connection.call(
            "update",
            "resp_botInvitedJoinGroupRequestEvent",
            {
                "eventId": int(target.pattern["request"].split("@")[-1]),
                "fromId": int(target.pattern["member"]),
                "groupId": int(target.pattern["group"]),
                "operate": 1,
                "message": reason or "",
            },
        )
