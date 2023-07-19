from __future__ import annotations

import base64
import io
import os
from datetime import datetime
from typing import TYPE_CHECKING

from avilla.core.builtins.capability import CoreCapability
from avilla.core.ryanvk.collector.account import AccountCollector
from avilla.core.selector import Selector
from avilla.standard.qq.announcement import (
    Announcement,
    AnnouncementDelete,
    AnnouncementPublish,
)

if TYPE_CHECKING:
    from ...account import ElizabethAccount  # noqa
    from ...protocol import ElizabethProtocol  # noqa


class ElizabethAnnouncementActionPerform((m := AccountCollector["ElizabethProtocol", "ElizabethAccount"]())._):
    m.post_applying = True

    @CoreCapability.pull.collect(m, "land.group.announcement", Announcement)
    async def get_announcement(self, target: Selector) -> Announcement:
        group = Selector().land(self.account.route["land"]).group(target.pattern["group"])
        for data in await self.account.connection.call(
            "fetch", "anno_list", {"id": int(target.pattern["group"]), "offset": 0, "size": 100}
        ):
            if str(data["fid"]) == target.pattern["announcement"]:
                return Announcement(
                    data["fid"],
                    group,
                    group.member(data["senderId"]),
                    content=data["content"],
                    all_confirmed=data["allConfirmed"],
                    confirmed_members=data["confirmedMembersCount"],
                    time=datetime.fromtimestamp(data["publicationTime"]),
                )
        raise KeyError(f"Announcement {target.pattern['announcement']} not found")

    @AnnouncementPublish.publish.collect(m, "land.group")
    async def publish_announcement(
        self,
        target: Selector,
        content: str,
        *,
        send_to_new_member: bool = False,
        pinned: bool = False,
        show_edit_card: bool = False,
        show_popup: bool = False,
        require_confirmation: bool = False,
        image: str | bytes | os.PathLike | io.IOBase | None = None,
    ) -> Selector:
        data = {
            "target": int(target.pattern["group"]),
            "content": content,
            "sendToNewMember": send_to_new_member,
            "pinned": pinned,
            "showEditCard": show_edit_card,
            "showPopup": show_popup,
            "requireConfirmation": require_confirmation,
        }
        if image is not None:
            if isinstance(image, bytes):
                data["imageBase64"] = base64.b64encode(image).decode("ascii")
            elif isinstance(image, os.PathLike):
                data["imageBase64"] = base64.b64encode(open(image, "rb").read()).decode("ascii")
            elif isinstance(image, io.IOBase):
                data["imageBase64"] = base64.b64encode(image.read()).decode("ascii")
            elif isinstance(image, str):
                data["imageUrl"] = image
        result = await self.account.connection.call("update", "anno_publish", data)
        return target.announcement(str(result["fid"]))

    @AnnouncementDelete.delete.collect(m, "land.group.announcement")
    async def delete_announcement(self, target: Selector):
        await self.account.connection.call(
            "update",
            "anno_delete",
            {"id": int(target.pattern["group"]), "fid": int(target.pattern["announcement"])},
        )
