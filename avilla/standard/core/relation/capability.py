from __future__ import annotations

from typing import Literal

from avilla.core.ryanvk import Capability, Fn, TargetFn
from avilla.core.selector import Selector


class SceneCapability(Capability):
    @TargetFn
    async def leave(self) -> None:
        ...

    @TargetFn
    async def disband(self) -> None:
        ...

    @TargetFn
    async def remove_member(self, reason: str | None = None) -> None:
        ...

    # @TargetFn
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
    @TargetFn
    async def terminate(self) -> None:
        # TODO: use wand
        ...
