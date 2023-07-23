from __future__ import annotations

import io
import os

from avilla.core.ryanvk import Capability, TargetFn
from avilla.core.selector import Selector


class AnnouncementPublish(Capability):
    @TargetFn
    async def publish(
        self,
        content: str,
        *,
        send_to_new_member: bool = False,
        pinned: bool = False,
        show_edit_card: bool = False,
        show_popup: bool = False,
        require_confirmation: bool = False,
        image: str | bytes | os.PathLike | io.IOBase | None = None,
    ) -> Selector:
        """发布群公告

        target 是公告发布到的群
        """
        ...


class AnnouncementDelete(Capability):
    @TargetFn
    async def delete(self) -> None:
        """删除群公告

        target 是群公告的 id
        """
        ...
