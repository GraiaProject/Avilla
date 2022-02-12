from typing import TYPE_CHECKING, List, cast

from avilla.core.selectors import entity as entity_selector
from avilla.core.service.entity import ExportInterface, Status
from avilla.onebot.connection import OnebotConnection

if TYPE_CHECKING:
    from .service import OnebotService


class OnebotInterface(ExportInterface):
    service: "OnebotService"

    def __init__(self, service: "OnebotService") -> None:
        self.service = service

    async def action(self, account: entity_selector, act: str, params: dict) -> dict:
        account = account.without_group()
        if account not in self.service.accounts:
            raise ValueError(f"Account {account} is not online")
        stat = cast(Status, self.service.get_status(account))
        if not stat.available:
            raise RuntimeError(f"Account {account} is not available")
        conns = self.service.accounts[account]
        if "action" not in conns:
            raise RuntimeError(f"Account {account} cannot perform actions")
        actor = cast(OnebotConnection, conns["action"])
        conf = self.service.protocol.avilla.get_config(self.service.__class__, account)
        timeout = None
        if conf:
            timeout = conf.resp_timeout
        else:
            conf = self.service.protocol.avilla.get_config(self.service.__class__)
            if conf:
                timeout = conf.resp_timeout
        return await actor.action(act, params, timeout=timeout)

    def is_available(self, account: entity_selector) -> bool:
        account = account.without_group()
        if account not in self.service.accounts:
            return False
        stat = cast(Status, self.service.get_status(account))
        return stat.available

    def get_status(self, account: entity_selector) -> Status:
        account = account.without_group()
        if account not in self.service.accounts:
            raise ValueError(f"Account {account} is not online")
        return self.service.get_status(account)

    def get_accounts(self) -> List[entity_selector]:
        return list(self.service.accounts.keys())
