from __future__ import annotations

from abc import ABCMeta, abstractmethod
from contextlib import asynccontextmanager
from typing import TYPE_CHECKING, Literal, Optional, Set

from launart.status import STAGE_STAT, STATS, Phase, ServiceStatus, U_Stage
from launart.utilles import any_completed

if TYPE_CHECKING:
    from launart.manager import Launart


class Service(metaclass=ABCMeta):
    id: str
    status: ServiceStatus
    manager: Optional[Launart] = None

    def __init__(self) -> None:
        self.status = ServiceStatus()

    @property
    @abstractmethod
    def required(self) -> Set[str]:
        ...

    @property
    @abstractmethod
    def stages(self) -> Set[Phase]:
        ...

    def ensure_manager(self, manager: Launart):
        if self.manager is not None and self.manager is not manager:
            raise RuntimeError("this component attempted to be mistaken a wrong ownership of launart/manager.")
        self.manager = manager

    @asynccontextmanager
    async def stage(self, stage: Literal["preparing", "blocking", "cleanup"]):
        if self.manager is None:
            raise RuntimeError("attempted to set stage of a component without a manager.")
        if self.manager.status.stage is None:
            raise LookupError("attempted to set stage of a component without a current manager")
        if stage not in self.stages:
            raise ValueError(f"undefined and unexpected stage entering: {stage}")

        if stage == "preparing":
            if "waiting-for-prepare" not in STAGE_STAT[self.status.stage]:
                raise ValueError(f"unexpected stage entering: {self.status.stage} -> waiting-for-prepare")
            await self.manager.status.wait_for_preparing()
            self.status.stage = "waiting-for-prepare"
            await self.status.wait_for("preparing")
            yield
            self.status.stage = "prepared"
        elif stage == "blocking":
            if "blocking" not in STAGE_STAT[self.status.stage]:
                raise ValueError(f"unexpected stage entering: {self.status.stage} -> blocking")
            await self.manager.status.wait_for_blocking()
            await self.wait_for_required()
            self.status.stage = "blocking"
            yield
            self.status.stage = "blocking-completed"
        elif stage == "cleanup":
            if "waiting-for-cleanup" not in STAGE_STAT[self.status.stage]:
                raise ValueError(f"unexpected stage entering: {self.status.stage} -> waiting-for-cleanup")
            await self.manager.status.wait_for_cleaning(current=self.id)
            self.status.stage = "waiting-for-cleanup"
            await self.status.wait_for("cleanup")
            yield
            self.status.stage = "finished"
        else:
            raise ValueError(f"entering unexpected stage: {stage}(unknown definition)")

    async def wait_for_required(self, stage: U_Stage = "prepared"):
        await self.wait_for(stage, *self.required)

    async def wait_for(self, stage: U_Stage, *component_id: str | type[Service]):
        if self.manager is None:
            raise RuntimeError("attempted to wait for some components without a manager.")
        components = [self.manager.get_component(id) for id in component_id]
        while any(component.status.stage not in STATS[STATS.index(stage) :] for component in components):
            await any_completed(
                *[component.status.wait_for_update() for component in components if component.status.stage != stage]
            )

    @abstractmethod
    async def launch(self, manager: Launart):
        pass
