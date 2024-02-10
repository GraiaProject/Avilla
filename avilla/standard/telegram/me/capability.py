from typing import Literal

from avilla.core import Selector
from avilla.core.ryanvk import TargetOverload
from avilla.standard.telegram.constants import BotCommandScope
from graia.ryanvk import Capability, Fn


class MeCapability(Capability):
    @Fn.complex({TargetOverload(): ["target"]})
    async def get_me(self, target: Selector) -> ...:
        ...

    @Fn.complex({TargetOverload(): ["target"]})
    async def get_my_commands(
        self, target: Selector, *, scope: BotCommandScope = None, language_code: str = None
    ) -> ...:
        ...

    @Fn.complex({TargetOverload(): ["target"]})
    async def get_my_description(self, target: Selector, *, language_code: str = None) -> str:
        ...

    @Fn.complex({TargetOverload(): ["target"]})
    async def get_my_short_description(self, target: Selector, *, language_code: str = None) -> str:
        ...

    @Fn.complex({TargetOverload(): ["target"]})
    async def get_my_name(self, target: Selector, *, language_code: str = None) -> str:
        ...

    @Fn.complex({TargetOverload(): ["target"]})
    async def set_webhook(
        self,
        target: Selector,
        *,
        url: str,
        max_connections: int = None,
        allowed_updates: list[str] = None,
        drop_pending_updates: bool = None,
        ip_address: str = None,
        certificate: ... = None,
    ) -> Literal[True]:
        pass

    @Fn.complex({TargetOverload(): ["target"]})
    async def delete_webhook(self, target: Selector, *, drop_pending_updates: bool = None) -> Literal[True]:
        pass

    @Fn.complex({TargetOverload(): ["target"]})
    async def get_webhook_info(self, target: Selector) -> ...:
        pass
