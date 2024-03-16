from graia.ryanvk import Capability, Fn


class PreferenceCapability(Capability):
    @Fn
    async def set_webhook(
        self,
        *,
        url: str,
        max_connections: int = None,
        allowed_updates: list[str] = None,
        drop_pending_updates: bool = None,
        ip_address: str = None,
        certificate: ... = None,
    ) -> None:
        pass

    @Fn
    async def delete_webhook(self, *, drop_pending_updates: bool = None) -> None:
        pass
