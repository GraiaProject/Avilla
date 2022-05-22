from __future__ import annotations

from contextlib import asynccontextmanager
from typing import TYPE_CHECKING

from graia.broadcast.entities.dispatcher import BaseDispatcher
from graia.broadcast.interfaces.dispatcher import DispatcherInterface
from loguru import logger

if TYPE_CHECKING:
    from avilla.core import Avilla
    from avilla.core.execution import Execution
    from avilla.core.relationship import Relationship

class AvillaBuiltinDispatcher(BaseDispatcher):
    avilla: Avilla

    def __init__(self, avilla: Avilla) -> None:
        self.avilla = avilla

    async def catch(self, interface: DispatcherInterface):
        if interface.annotation is Avilla:
            return self.avilla
        elif interface.annotation in self.avilla._protocol_map:
            return self.avilla._protocol_map[interface.annotation]


@asynccontextmanager
async def execute_target_ensure(rs: Relationship, exec: Execution):
    if not exec.located:
        if exec.locate_type == "mainline":
            exec.locate_target(rs.mainline)
        elif exec.locate_type == "ctx":
            exec.locate_target(rs.ctx)
        elif exec.locate_type == "via":
            if rs.via is None:
                logger.warning("relationship's via is None, skip locate")
                return
            exec.locate_target(rs.via)
        elif exec.locate_type == "current":
            exec.locate_target(rs.current)
        else:
            logger.warning(f"unknown locate_type: {exec} - {exec.locate_type}")
    yield