from __future__ import annotations

from typing import TYPE_CHECKING

from launart import Launart, Service, any_completed

if TYPE_CHECKING:
    from avilla.telegram.connection.poll import TelegramLongPollingNetworking
    from avilla.telegram.protocol import TelegramProtocol


class TelegramService(Service):
    id = "telegram.service"
    required: set[str] = set()
    stages: set[str] = {"preparing", "blocking", "cleanup"}

    protocol: TelegramProtocol
    connection_map: dict[int, TelegramLongPollingNetworking]

    def __init__(self, protocol: TelegramProtocol) -> None:
        super().__init__()
        self.protocol = protocol
        self.connection_map = {}

    def has_connection(self, account_id: int):
        return account_id in self.connection_map

    def get_connection(self, account_id: int) -> TelegramLongPollingNetworking:
        return self.connection_map[account_id]

    async def launch(self, manager: Launart):
        async with self.stage("preparing"):
            for i in self.connection_map.values():
                manager.add_component(i)

        async with self.stage("blocking"):
            await any_completed(
                manager.status.wait_for_sigexit(),
                *(i.status.wait_for("blocking-completed") for i in self.connection_map.values()),
            )

        async with self.stage("cleanup"):
            ...
