from __future__ import annotations

from flywheel import InstanceOf
from satori.client.account import Account

from .account import SatoriAccount
from .protocol import SatoriProtocol


class InstanceOfProtocol:
    protocol = InstanceOf(SatoriProtocol)


class InstanceOfAccount(InstanceOfProtocol):
    account = InstanceOf(SatoriAccount)


class InstanceOfConnection(InstanceOfProtocol):
    connection = InstanceOf(Account)
