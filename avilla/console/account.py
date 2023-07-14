from __future__ import annotations

from typing import TYPE_CHECKING

from avilla.core.account import AccountStatus, BaseAccount, AccountInfo
from avilla.core.selector import Selector
from avilla.core.platform import Abstract, Land, Platform
from .staff import ConsoleStaff

if TYPE_CHECKING:
    from .protocol import ConsoleProtocol

platform = Platform(
    Land(
        "console",
        [{"name": "GraiaxCommunity"}],
        humanized_name="Avilla-Console - Console Impl for avilla",
    ),
    Abstract(
        protocol="Console",
        maintainers=[{"name": "yanyongyu"}],
        humanized_name="Textual Console",
    )
)

class ConsoleAccount(BaseAccount):
    protocol: ConsoleProtocol
    status: AccountStatus

    def __init__(self, protocol: ConsoleProtocol):
        super().__init__(Selector().land("console").account(protocol.name), protocol.avilla)
        self.protocol = protocol
        self.status = AccountStatus()
        self.protocol.avilla.accounts[self.route] = AccountInfo(
            self.route, self, self.protocol, platform
        )

    @property
    def staff(self):
        return ConsoleStaff(self)

    @property
    def client(self):
        return self.protocol.service.app

    @property
    def available(self) -> bool:
        return self.status.enabled
