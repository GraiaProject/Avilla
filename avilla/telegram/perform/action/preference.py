from __future__ import annotations

from typing import TYPE_CHECKING

from avilla.core.ryanvk.collector.account import AccountCollector
from avilla.standard.telegram.preference.capability import PreferenceCapability

if TYPE_CHECKING:
    from avilla.telegram.account import TelegramAccount  # noqa
    from avilla.telegram.protocol import TelegramProtocol  # noqa


class TelegramPreferenceActionPerform((m := AccountCollector["TelegramProtocol", "TelegramAccount"]())._):
    m.namespace = "avilla.protocol/telegram::action"
    m.identify = "preference"

    @m.entity(PreferenceCapability.set_webhook)
    async def set_webhook(
        self,
        *,
        url: str,
        max_connections: int = None,
        allowed_updates: list[str] = None,
        drop_pending_updates: bool = None,
        ip_address: str = None,
        certificate: ... = None,
        secret_token: str = None,
    ):
        await self.account.connection.call(
            "setWebhook",
            url=url,
            max_connections=max_connections,
            allowed_updates=allowed_updates,
            drop_pending_updates=drop_pending_updates,
            ip_address=ip_address,
            certificate=certificate,
            secret_token=secret_token,
        )

    @m.entity(PreferenceCapability.delete_webhook)
    async def delete_webhook(self, *, drop_pending_updates: bool = None):
        await self.account.connection.call("deleteWebhook", drop_pending_updates=drop_pending_updates)
