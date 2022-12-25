from __future__ import annotations

from typing import TYPE_CHECKING

from graia.broadcast import Broadcast
from launart import Launart

from avilla.core._runtime import get_current_avilla
from avilla.core.account import AbstractAccount
from avilla.core.dispatchers import AvillaBuiltinDispatcher
from avilla.core.platform import Land
from avilla.core.protocol import BaseProtocol
from avilla.core.resource import LocalFileResource
from avilla.core.selector import Selector
from avilla.core.service import AvillaService
from avilla.core.trait.signature import ResourceFetch

from .trait.context import wrap_artifacts

if TYPE_CHECKING:
    from avilla.core.trait.signature import ArtifactSignature


class Avilla:
    broadcast: Broadcast
    launch_manager: Launart
    protocols: list[BaseProtocol]
    accounts: list[AbstractAccount]
    service: AvillaService

    with wrap_artifacts() as global_artifacts:
        import avilla.core.builtins.resource_fetch as _

    def __init__(
        self,
        broadcast: Broadcast,
        launch_manager: Launart,
        protocols: list[BaseProtocol],
    ):
        if len({type(i) for i in protocols}) != len(protocols):
            raise ValueError("protocol must be unique, and the config should be passed by config.")

        self.broadcast = broadcast
        self.launch_manager = launch_manager
        self.protocols = protocols
        self._protocol_map = {type(i): i for i in protocols}
        self.accounts = []
        self.global_artifacts = {}
        self.service = AvillaService(self)

        self.launch_manager.add_service(self.service)

        for protocol in self.protocols:
            # Ensureable 用于注册各种东西，包括 Service, ResourceProvider 等。
            protocol.ensure(self)

        self.broadcast.finale_dispatchers.append(AvillaBuiltinDispatcher(self))

        @self.register_global_artifact(ResourceFetch(LocalFileResource))
        async def _fetch_local_file(_, res: LocalFileResource):
            return res.file.read_bytes()

    @classmethod
    def current(cls) -> "Avilla":
        return get_current_avilla()

    @property
    def loop(self):
        return self.broadcast.loop

    def register_global_artifact(self, signature: ArtifactSignature):
        def wrapper(v):
            self.global_artifacts[signature] = v
            return v

        return wrapper

    def add_account(self, account: AbstractAccount):
        if account in self.accounts:
            raise ValueError("account already exists.")
        self.accounts.append(account)

    def remove_account(self, account: AbstractAccount):
        if account not in self.accounts:
            raise ValueError("account not exists.")
        self.accounts.remove(account)

    def get_account(
        self, account_id: str | None = None, selector: Selector | None = None, land: Land | None = None
    ) -> AbstractAccount | None:
        for account in self.accounts:
            if account_id is not None and account.id != account_id:
                continue
            if selector is not None and not selector.matches(account.to_selector()):
                continue
            if land is not None and account.land != land:
                continue
            return account

    def get_accounts(
        self, account_id: str | None = None, selector: Selector | None = None, land: Land | None = None
    ) -> list[AbstractAccount]:
        result = []
        for account in self.accounts:
            if account_id is not None and account.id != account_id:
                continue
            if selector is not None and not selector.matches(account.to_selector()):
                continue
            if land is not None and account.land != land:
                continue
            result.append(account)
        return result
