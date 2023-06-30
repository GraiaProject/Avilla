from __future__ import annotations

from contextvars import ContextVar
from typing import TYPE_CHECKING

from .common.isolate import Isolate

if TYPE_CHECKING:
    from avilla.core.application import Avilla

    from ..protocol import BaseProtocol

processing_protocol: ContextVar[type[BaseProtocol]] = ContextVar("processing_protocol")
processing_isolate: ContextVar[Isolate] = ContextVar("processing_isolate")
processing_application: ContextVar[Avilla] = ContextVar("processing_application")
