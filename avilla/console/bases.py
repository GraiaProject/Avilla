from __future__ import annotations

from flywheel import InstanceOf
from .protocol import ConsoleProtocol
from .account import ConsoleAccount

class InstanceOfProtocol:
    protocol = InstanceOf(ConsoleProtocol)

class InstanceOfAccount(InstanceOfProtocol):
    account = InstanceOf(ConsoleAccount)
