from typing import TYPE_CHECKING, Type

from sqlalchemy.ext.asyncio import AsyncEngine, create_async_engine
from sqlmodel import SQLModel

from avilla.core.launch import LaunchComponent
from avilla.core.service import Service
from avilla.core.service.entity import ExportInterface

if TYPE_CHECKING:
    from avilla.core import Avilla


class EngineProvider(ExportInterface):
    engine: AsyncEngine

    def __init__(self, engine: AsyncEngine):
        self.engine = engine

    def get(self) -> AsyncEngine:
        return self.engine


class SqlmodelService(Service):
    supported_interface_types = {EngineProvider}
    supported_description_types = set()

    url: str
    engine: AsyncEngine

    def __init__(self, url: str) -> None:
        self.url = url
        self.engine = create_async_engine(self.url, future=True)
        super().__init__()

    def get_interface(self, interface_type: Type[EngineProvider]):
        return EngineProvider(self.engine)

    def get_status(self, entity):
        raise NotImplementedError

    def set_status(self, entity, available: bool, description: str):
        raise NotImplementedError

    def set_current_status(self, available: bool, description: str):
        raise NotImplementedError

    async def launch_prepare(self, avilla: "Avilla"):
        async with self.engine.begin() as conn:
            await conn.run_sync(SQLModel.metadata.create_all)

    async def launch_cleanup(self, avilla: "Avilla"):
        await self.engine.dispose()

    @property
    def launch_component(self) -> LaunchComponent:
        return LaunchComponent(
            "storage.sqlmodel",
            set(),
            prepare=self.launch_prepare,
            cleanup=self.launch_cleanup,
        )
