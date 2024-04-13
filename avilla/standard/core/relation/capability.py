from __future__ import annotations

from typing import Literal

from avilla.core.ryanvk import Capability, Fn, TargetOverload
from avilla.core.selector import Selector


class SceneCapability(Capability):
    @Fn.complex({TargetOverload(): ["target"]})
    async def leave(self, target: Selector) -> None:
        ...

    @Fn.complex({TargetOverload(): ["target"]})
    async def disband(self, target: Selector) -> None:
        ...

    @Fn.complex({TargetOverload(): ["target"]})
    async def remove_member(self, target: Selector, reason: str | None = None, permanent: bool = False) -> None:
        ...

    # @Fn.with_overload({
    #    TargetOverload(): ['target']
    # })
    # async def request_join(self, solver: Isolate) -> None:
    #     ...

    # TODO: invite someone to join the scene


class RequestJoinCapability(Capability):
    @Fn
    async def on_question(self, target: Selector, question_id: str, question: str, optional: bool) -> str | None:
        ...

    @Fn
    async def on_reason(self, target: Selector) -> str | None:
        ...

    @Fn
    async def on_term(self, term: tuple[Literal["string", "url"] | str, str]) -> bool:
        ...


class RelationshipTerminate(Capability):
    @Fn.complex({TargetOverload(): ["target"]})
    async def terminate(self, target: Selector) -> None:
        # TODO: use wand
        ...
