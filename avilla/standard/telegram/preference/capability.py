from __future__ import annotations

from pathlib import Path

from graia.ryanvk import Capability, Fn


class PreferenceCapability(Capability):
    @Fn
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
    ) -> None:
        pass

    @Fn
    async def delete_webhook(self, *, drop_pending_updates: bool = None) -> None:
        pass
