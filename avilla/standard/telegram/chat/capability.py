from __future__ import annotations

from typing import Literal

from avilla.core import Selector
from avilla.core.ryanvk import TargetOverload
from graia.ryanvk import Capability, Fn


class ChatCapability(Capability):
    @Fn.complex({TargetOverload(): ["target"]})
    async def pin_message(self, target: Selector, disable_notification: bool = False) -> None: ...

    @Fn.complex({TargetOverload(): ["target"]})
    async def unpin_message(self, target: Selector) -> None: ...

    @Fn.complex({TargetOverload(): ["target"]})
    async def unpin_all_messages(self, target: Selector) -> None: ...

    @Fn.complex({TargetOverload(): ["target"]})
    async def set_group_sticker_set(self, target: Selector, sticker_set_name: str) -> None: ...

    @Fn.complex({TargetOverload(): ["target"]})
    async def delete_group_sticker_set(self, target: Selector) -> None: ...

    @Fn.complex({TargetOverload(): ["target"]})
    async def delete_topic(self, target: Selector) -> None: ...

    @Fn.complex({TargetOverload(): ["target"]})
    async def edit_topic(
        self,
        target: Selector,
        *,
        name: str | None = None,
        icon_custom_emoji_id: str | None = None,
    ) -> None: ...

    @Fn.complex({TargetOverload(): ["target"]})
    async def close_topic(self, target: Selector) -> None: ...

    @Fn.complex({TargetOverload(): ["target"]})
    async def create_topic(
        self,
        target: Selector,
        name: str,
        *,
        icon_color: Literal[7322096, 16766590, 13338331, 9367192, 16749490, 16478047] | None = None,
        # See [API Docs](https://core.telegram.org/bots/api#createforumtopic) for the meaning of these values
        icon_custom_emoji_id: str | None = None,
    ) -> None: ...

    @Fn.complex({TargetOverload(): ["target"]})
    async def reopen_topic(self, target: Selector) -> None: ...

    @Fn.complex({TargetOverload(): ["target"]})
    async def edit_general_topic(self, target: Selector, name: str) -> None: ...

    @Fn.complex({TargetOverload(): ["target"]})
    async def close_general_topic(self, target: Selector) -> None: ...

    @Fn.complex({TargetOverload(): ["target"]})
    async def reopen_general_topic(self, target: Selector) -> None: ...

    @Fn.complex({TargetOverload(): ["target"]})
    async def hide_general_topic(self, target: Selector) -> None: ...

    @Fn.complex({TargetOverload(): ["target"]})
    async def unhide_general_topic(self, target: Selector) -> None: ...
