from contextlib import asynccontextmanager
from typing import Any, AsyncGenerator

from aiohttp import ClientSession

from avilla.core.launch import LaunchComponent
from avilla.core.network.aiohttp.schema import ClientSchema, HttpRequestSchema
from avilla.core.network.builtins.partitions import GetCookie, GetHeader, Read
from avilla.core.network.endpoint import Endpoint
from avilla.core.network.service import PolicyProtocol, Service, ServiceId


def as_async(func):
    async def wrapper(*args, **kwargs):
        return func(*args, **kwargs)

    return wrapper


class AiohttpHttpClient(Service[ClientSchema, Any]):
    id = ServiceId("org.graia", "avilla.core", "http", "client")
    _aiohttp_session: ClientSession

    def __init__(self, session: ClientSession = None) -> None:
        self._aiohttp_session = session or ClientSession()
        super().__init__()

    @property
    def launch_component(self) -> LaunchComponent:
        return LaunchComponent(
            self.id.avilla_uri,
            set(),
            self.launch_mainline,
            self.launch_prepare,
            self.launch_cleanup,
        )

    def create_connection_obj(self) -> str:
        return super().create_connection_obj()

    def destroy_connection_obj(self, connection_id: str) -> None:
        return super().destroy_connection_obj(connection_id)

    def register_endpoint(self, schema: ClientSchema, policy: Any) -> Endpoint[ClientSchema, Any]:
        return super().register_endpoint(schema, policy)

    def remove_endpoint(self, endpoint: Endpoint[ClientSchema, Any]) -> None:
        return super().remove_endpoint(endpoint)

    async def launch_cleanup(self):
        await self._aiohttp_session.close()

    @asynccontextmanager
    async def postconnect(self, schema: HttpRequestSchema) -> AsyncGenerator[PolicyProtocol, None]:
        if isinstance(schema, HttpRequestSchema):
            async with self._aiohttp_session.request(
                schema.method,
                schema.url,
                headers=schema.headers,
                data=schema.data,
            ) as response:
                yield PolicyProtocol(
                    Endpoint(None, schema),  # type: ignore
                    partition_handlers={
                        Read: lambda x: response.read(),
                        GetHeader: as_async(lambda x: response.headers.get(x.key)),
                        GetCookie: as_async(lambda x: response.cookies.get(x.key)),
                    },
                    activity_handlers={},
                )
