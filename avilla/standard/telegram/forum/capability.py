from avilla.core import Selector
from avilla.core.ryanvk import TargetOverload
from graia.ryanvk import Capability, Fn


class ForumCapability(Capability):
    @Fn.complex({TargetOverload(): ["target"]})
    async def delete_topic(self, target: Selector) -> None:
        ...

    @Fn.complex({TargetOverload(): ["target"]})
    async def edit_topic(
        self,
        target: Selector,
        *,
        name: str = None,
        icon_custom_emoji_id: str = None,
    ) -> None:
        ...

    @Fn.complex({TargetOverload(): ["target"]})
    async def close_topic(self, target: Selector) -> None:
        ...

    @Fn.complex({TargetOverload(): ["target"]})
    async def create_topic(
        self,
        target: Selector,
        name: str,
        *,
        icon_color: int = None,
        icon_custom_emoji_id: str = None,
    ) -> None:
        ...

    @Fn.complex({TargetOverload(): ["target"]})
    async def reopen_topic(self, target: Selector) -> None:
        ...

    @Fn.complex({TargetOverload(): ["target"]})
    async def edit_general_topic(self, target: Selector, name: str) -> None:
        ...

    @Fn.complex({TargetOverload(): ["target"]})
    async def close_general_topic(self, target: Selector) -> None:
        ...

    @Fn.complex({TargetOverload(): ["target"]})
    async def reopen_general_topic(self, target: Selector) -> None:
        ...

    @Fn.complex({TargetOverload(): ["target"]})
    async def hide_general_topic(self, target: Selector) -> None:
        ...

    @Fn.complex({TargetOverload(): ["target"]})
    async def unhide_general_topic(self, target: Selector) -> None:
        ...
