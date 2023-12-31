from avilla.core.ryanvk import TargetOverload
from avilla.standard.telegram.constants import BotCommandScope
from graia.ryanvk import Capability, Fn


class MeCapability(Capability):
    @Fn.complex({TargetOverload(): ["target"]})
    async def get_me(self) -> ...:
        ...

    @Fn.complex({TargetOverload(): ["target"]})
    async def get_my_commands(self, *, scope: BotCommandScope = None, language_code: str = None) -> ...:
        ...

    @Fn.complex({TargetOverload(): ["target"]})
    async def get_my_description(self, *, language_code: str = None) -> str:
        ...

    @Fn.complex({TargetOverload(): ["target"]})
    async def get_my_short_description(self, *, language_code: str = None) -> str:
        ...

    @Fn.complex({TargetOverload(): ["target"]})
    async def get_my_name(self, *, language_code: str = None) -> str:
        ...

    # TODO set_*
