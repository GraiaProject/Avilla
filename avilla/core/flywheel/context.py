from __future__ import annotations

from contextlib import contextmanager
from typing import TYPE_CHECKING, Any

from .typing import TEntity

if TYPE_CHECKING:
    from .fn.record import FnImplement, FnRecord


class CollectContext:
    fn_implements: dict[FnImplement, FnRecord]

    def __init__(self):
        self.fn_implements = {}

    def collect(self, entity: TEntity) -> TEntity:
        return entity.collect(self)

    @contextmanager
    def collect_scope(self):
        from .globals import COLLECTING_CONTEXT_VAR

        token = COLLECTING_CONTEXT_VAR.set(self)
        try:
            yield self
        finally:
            COLLECTING_CONTEXT_VAR.reset(token)

    @contextmanager
    def lookup_scope(self):
        from .globals import LOOKUP_LAYOUT_VAR

        token = LOOKUP_LAYOUT_VAR.set((self, *LOOKUP_LAYOUT_VAR.get()))
        try:
            yield self
        finally:
            LOOKUP_LAYOUT_VAR.reset(token)


class InstanceContext:
    instances: dict[type, Any]

    def __init__(self):
        self.instances = {}

    @contextmanager
    def scope(self, *, inherit: bool = True):
        from .globals import INSTANCE_CONTEXT_VAR

        original = self.instances
        if inherit:
            self.instances = {**INSTANCE_CONTEXT_VAR.get().instances, **self.instances}

        token = INSTANCE_CONTEXT_VAR.set(self)
        try:
            yield self
        finally:
            INSTANCE_CONTEXT_VAR.reset(token)
            self.instances = original
