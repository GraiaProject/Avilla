from __future__ import annotations

from flywheel import InstanceOf
from avilla.core.ryanvk.bases import InstanceOfAvilla
from avilla.onebot.v11.protocol import OneBot11Protocol
from avilla.onebot.v11.account import OneBot11Account

class InstanceOfProtocol(InstanceOfAvilla):
    protocol = InstanceOf(OneBot11Protocol)

class InstanceOfAccount(InstanceOfProtocol):
    account = InstanceOf(OneBot11Account)
