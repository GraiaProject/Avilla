from __future__ import annotations

from typing import TYPE_CHECKING

from launart import Launart, Service, any_completed

if TYPE_CHECKING:
    from avilla.telegram.bot.bot import TelegramBot
    from avilla.telegram.protocol import TelegramProtocol


class TelegramService(Service):
    id = "telegram.service"
    required: set[str] = set()
    stages: set[str] = {"preparing", "blocking", "cleanup"}

    protocol: TelegramProtocol
    instances: list[TelegramBot]
    instance_map: dict[int, TelegramBot]

    def __init__(self, protocol: TelegramProtocol) -> None:
        super().__init__()
        self.protocol = protocol
        self.instances = []
        self.instance_map = {}

    def has_instance(self, account_id: int):
        return account_id in self.instance_map

    def get_instance(self, account_id: int) -> TelegramBot:
        return self.instance_map[account_id]

    async def launch(self, manager: Launart):
        async with self.stage("preparing"):
            for i in self.instances:
                manager.add_component(i)

        async with self.stage("blocking"):
            await any_completed(
                manager.status.wait_for_sigexit(), *(i.status.wait_for("blocking-completed") for i in self.instances)
            )

        async with self.stage("cleanup"):
            ...
