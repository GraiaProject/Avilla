from __future__ import annotations

from contextlib import asynccontextmanager
from typing import TYPE_CHECKING

from avilla.core.context import ctx_target
from avilla.core.execution import Execution
from avilla.core.typing import T_Target

if TYPE_CHECKING:
    from avilla.core.relationship import Relationship


def target_context_injector(rs: "Relationship", exec_: Execution):
    @asynccontextmanager
    async def wrapper():
        if exec_.__class__._auto_detect_target:
            with ctx_target.use(rs.ctx):
                yield
        else:
            yield

    return wrapper()


def useTarget(target: T_Target):
    @asynccontextmanager
    async def target_injector(rs: "Relationship", exec: Execution):
        with ctx_target.use(target):
            yield

    return target_injector
