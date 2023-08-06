from __future__ import annotations

import asyncio
from typing import Literal, Optional, Union

from statv import Stats, Statv

from launart._sideload import FutureMark

U_ManagerStage = Literal["preparing", "blocking", "cleaning", "finished"]
U_Stage = Union[
    Literal[
        "waiting-for-prepare",
        "preparing",
        "prepared",
        "blocking",
        "blocking-completed",
        "waiting-for-cleanup",
        "cleanup",
        "finished",
    ],
    None,
]
Phase = Literal["preparing", "blocking", "cleanup"]
STAGE_STAT = {
    None: {"waiting-for-prepare", "waiting-for-cleanup", "blocking", "finished"},
    "waiting-for-prepare": {"preparing"},
    "preparing": {"prepared"},
    "prepared": {"blocking", "waiting-for-cleanup", "finished"},
    "blocking": {"blocking-completed"},
    "blocking-completed": {"waiting-for-cleanup", "finished"},
    "waiting-for-cleanup": {"cleanup"},
    "cleanup": {"finished"},
    "finished": {None},
}
STATS = [
    None,
    "waiting-for-prepare",
    "preparing",
    "prepared",
    "blocking",
    "blocking-completed",
    "waiting-for-cleanup",
    "cleanup",
    "finished",
]


class ManagerStatus(Statv):
    stage = Stats[Optional[U_ManagerStage]]("U_ManagerStage", default=None)
    exiting = Stats[bool]("exiting", default=False)

    def __init__(self) -> None:
        super().__init__()

    def __repr__(self) -> str:
        return f"<ManagerStatus stage={self.stage} waiters={len(self._waiters)}>"

    @property
    def preparing(self) -> bool:
        return self.stage == "preparing"

    @property
    def blocking(self) -> bool:
        return self.stage == "blocking"

    @property
    def cleaning(self) -> bool:
        return self.stage == "cleaning"

    async def wait_for_update(self, *, current: str | None = None, stage: U_ManagerStage | None = None):
        waiter = asyncio.Future()
        if current is not None:
            waiter.add_done_callback(FutureMark(current, stage))
        self._waiters.append(waiter)
        try:
            return await waiter
        finally:
            self._waiters.remove(waiter)

    async def wait_for_preparing(self):
        while not self.preparing:
            await self.wait_for_update()

    async def wait_for_blocking(self):
        while not self.blocking:
            await self.wait_for_update()

    async def wait_for_cleaning(self, *, current: str | None = None):
        while not self.cleaning:
            await self.wait_for_update(current=current, stage="cleaning")

    async def wait_for_finished(self, *, current: str | None = None):
        while self.stage not in {"finished", None}:
            await self.wait_for_update(current=current, stage="finished")

    async def wait_for_sigexit(self):
        while self.stage in {"preparing", "blocking"} and not self.exiting:
            await self.wait_for_update()


class ServiceStatus(Statv):
    stage = Stats[Optional[U_Stage]]("stage", default=None)

    def __init__(self) -> None:
        super().__init__()

    @property
    def prepared(self) -> bool:
        return self.stage in ("prepared", "blocking")

    @property
    def blocking(self) -> bool:
        return self.stage == "blocking"

    @property
    def finished(self) -> bool:
        return self.stage == "finished"

    @staticmethod
    @stage.validator
    def _(stats: Stats[U_Stage | None], past: U_Stage | None, current: U_Stage | None):
        if current not in STAGE_STAT[past]:
            raise ValueError(f"Invalid stage transition: {past} -> {current}")
        return current

    def unset(self) -> None:
        self.stage = None

    async def wait_for(self, stage: U_Stage = None):
        stages = set(STATS[STATS.index(stage) :])
        while self.stage not in stages:
            await self.wait_for_update()
