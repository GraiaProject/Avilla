from __future__ import annotations

from pathlib import Path
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
        max_connections: int | None = None,
        allowed_updates: list[str] | None = None,
        drop_pending_updates: bool | None = None,
        ip_address: str | None = None,
        certificate: Path | None = None,
        secret_token: str | None = None,
    ):
        if certificate:
            filename = certificate.stem
            file = {filename: (filename, certificate.read_bytes())}
            cert = f"attach://{filename}"
        else:
            file = None
            cert = None
        await self.account.connection.call(
            "setWebhook",
            url=url,
            max_connections=max_connections,
            allowed_updates=allowed_updates,
            drop_pending_updates=drop_pending_updates,
            ip_address=ip_address,
            certificate=cert,
            secret_token=secret_token,
            _file=file,
        )

    @m.entity(PreferenceCapability.delete_webhook)
    async def delete_webhook(self, *, drop_pending_updates: bool = None):
        await self.account.connection.call("deleteWebhook", drop_pending_updates=drop_pending_updates)
