import asyncio
import importlib.metadata
from contextlib import asynccontextmanager
from typing import Any, Awaitable, Callable, Dict, Generic, List, Optional, Set, Type, Union

from graia.broadcast import Broadcast
from graia.broadcast.interfaces.dispatcher import DispatcherInterface
from loguru import logger
from rich.console import Console
from rich.logging import RichHandler
from rich.status import Status
from avilla.core.config import ConfigApplicant, ConfigProvider, TModel, TScope

from avilla.core.context import ctx_avilla
from avilla.core.event import RelationshipDispatcher
from avilla.core.launch import LaunchComponent, resolve_requirements
from avilla.core.protocol import BaseProtocol
from avilla.core.resource import ResourceAccessor, ResourceMetaWrapper, ResourceProvider
from avilla.core.resource.activity import read
from avilla.core.selectors import resource as resource_selector
from avilla.core.service import Service, TInterface
from avilla.core.service.entity import ExportInterface
from avilla.core.typing import TConfig, TExecutionMiddleware, TProtocol
from graia.broadcast.entities.dispatcher import BaseDispatcher

from avilla.core.utilles import priority_strategy

AVILLA_ASCII_LOGO_AS_LIST = [
    "[bold]Avilla[/]: a universal asynchronous message flow solution, powered by [blue]Graia Project[/].",
    r"    _        _ _ _",
    r"   / \__   _(_) | | __ _",
    r"  / _ \ \ / / | | |/ _` |",
    r" / ___ \ V /| | | | (_| |",
    r"/_/   \_\_/ |_|_|_|\__,_|",
]

GRAIA_PROJECT_REPOS = ["avilla-core", "graia-broadcast", "graia-saya", "graia-scheduler"]


class Avilla:
    broadcast: Broadcast
    protocols: List[BaseProtocol]
    protocol_classes: List[Type[BaseProtocol]]

    launch_components: Dict[str, LaunchComponent]
    middlewares: List[TExecutionMiddleware]
    services: List[Service]
    resource_providers: List[ResourceProvider]

    _service_interfaces: Dict[Type[ExportInterface], Service]
    _res_provider_types: Dict[str, ResourceProvider]

    sigexit: asyncio.Event
    rich_console: Console

    def __init__(
        self,
        broadcast: Broadcast,
        protocols: List[Type[BaseProtocol]],
        services: List[Service],
        config: Dict[
            Union[ConfigApplicant[TModel], Type[ConfigApplicant[TModel]]],
            Union[TModel, Dict[TScope, Union[TModel, "ConfigProvider[TModel]"]]],
        ],
        default_config_provider: Type[ConfigProvider],
        middlewares: List[TExecutionMiddleware] = None,
    ):
        self.broadcast = broadcast
        self.protocol_classes = protocols
        self.protocols = [protocol(self) for protocol in protocols]
        self.services = services
        self._service_interfaces = priority_strategy(services, lambda s: s.supported_interface_types)
        self.middlewares = middlewares or []
        self.launch_components = {
            **({i.launch_component.id: i.launch_component for i in services}),
            **({protocol.launch_component.id: protocol.launch_component for protocol in self.protocols}),
        }
        self.sigexit = asyncio.Event()
        self.rich_console = Console()
        self.resource_providers = []

        for protocol in self.protocols:
            if isinstance(protocol, ResourceProvider):  # Protocol 可以作为资源提供方
                self.resource_providers.append(protocol)

        self._res_provider_types = priority_strategy(self.resource_providers, lambda p: p.supported_resource_types)
        self.broadcast.finale_dispatchers.append(RelationshipDispatcher())

        @self.broadcast.finale_dispatchers.append
        class AvillaBuiltinDispatcher(BaseDispatcher):
            @staticmethod
            async def catch(interface: DispatcherInterface):
                if interface.annotation is Avilla:
                    return self
                elif isinstance(interface.annotation, type) and issubclass(interface.annotation, BaseProtocol):
                    for protocol in self.protocol_classes:
                        if interface.annotation is protocol.__class__:
                            return protocol(self)

    @classmethod
    def current(cls) -> "Avilla":
        return ctx_avilla.get()

    def new_launch_component(
        self,
        id: str,
        requirements: Set[str] = None,
        mainline: Optional[Callable[["Avilla"], Awaitable[Any]]] = None,
        prepare: Callable[["Avilla"], Awaitable[Any]] = None,
        cleanup: Callable[["Avilla"], Awaitable[Any]] = None,
    ) -> LaunchComponent:
        component = LaunchComponent(id, requirements or set(), mainline, prepare, cleanup)
        self.launch_components[id] = component
        return component

    def remove_launch_component(self, id: str):
        if id not in self.launch_components:
            raise KeyError("id doesn't exist.")
        del self.launch_components[id]

    def add_service(self, service: Service):
        if service in self.services:
            raise ValueError("existed service")
        self.services.append(service)
        if isinstance(service, ResourceProvider):
            self.resource_providers.append(service)
            self._res_provider_types = priority_strategy(self.resource_providers, lambda p: p.supported_resource_types)
        launch_component = service.launch_component
        self.launch_components[launch_component.id] = launch_component

    def remove_service(self, service: Service):
        if service not in self.services:
            raise ValueError("service doesn't exist.")
        self.services.remove(service)
        if isinstance(service, ResourceProvider):
            self.resource_providers.remove(service)
            self._res_provider_types = priority_strategy(self.resource_providers, lambda p: p.supported_resource_types)
        del self.launch_components[service.launch_component.id]

    def get_interface(self, interface_type: Type[TInterface]) -> TInterface:
        if interface_type not in self._service_interfaces:
            raise ValueError(f"interface type {interface_type} not supported.")
        return self._service_interfaces[interface_type].get_interface(interface_type)

    @asynccontextmanager
    async def access_resource(self, resource: resource_selector):
        resource_type, resource_id = list(resource.path.items())[0]
        if resource_type not in self._res_provider_types:
            raise ValueError(f"resource type {resource_type} not supported.")
        provider = self._res_provider_types[resource_type]
        async with provider.access_resource(resource) as accessor:
            yield accessor

    async def fetch_resource(self, resource: resource_selector):
        async with self.access_resource(resource) as accessor:
            return await accessor.execute(read)

    def get_resource_meta(self, resource: resource_selector):
        resource_type, resource_id = list(resource.path.items())[0]
        if resource_type not in self._res_provider_types:
            raise ValueError(f"resource type {resource_type} not supported.")
        provider = self._res_provider_types[resource_type]
        

    async def launch(self):
        logger.configure(
            handlers=[
                {
                    "sink": RichHandler(console=self.rich_console, markup=True),
                    "format": "<green>{time:YYYY-MM-DD HH:mm:ss.SSS}</green> | <level>{level: <8}</level> | "
                    "<cyan>{name}</cyan>: <cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>",
                }
            ]
        )

        logger.info("\n".join(AVILLA_ASCII_LOGO_AS_LIST))
        for telemetry in GRAIA_PROJECT_REPOS:
            try:
                version = importlib.metadata.version(telemetry)
            except Exception:
                version = "unknown / not-installed"
            logger.info(f"[b cornflower_blue]{telemetry}[/] version: [cyan3]{version}[/]")

        for protocol in self.protocols:
            if protocol.__class__.platform is not BaseProtocol.platform:
                logger.info(f"using platform: {protocol.__class__.platform.universal_identifier}")

        for service in self.services:
            logger.info(f"using service: {service.__class__.__name__}")

        logger.info(f"launch components count: {len(self.launch_components)}")

        with Status("[orange bold]preparing components...", console=self.rich_console) as status:
            for component_layer in resolve_requirements(set(self.launch_components.values())):
                tasks = [
                    asyncio.create_task(component.prepare(self), name=component.id)
                    for component in component_layer
                    if component.prepare
                ]
                for task in tasks:
                    task.add_done_callback(lambda t: status.update(f"{t.get_name()} prepared."))
                await asyncio.wait(tasks)
            status.update("all launch components prepared.")
            await asyncio.sleep(1)

        logger.info("[green bold]components prepared, switch to mainlines and block main thread.")

        loop = asyncio.get_running_loop()
        tasks = [
            loop.create_task(component.mainline(self), name=component.id)
            for component in self.launch_components.values()
            if component.mainline
        ]
        for task in tasks:
            task.add_done_callback(lambda t: logger.info(f"mainline {t.get_name()} completed."))

        logger.info(f"mainline count: {len(tasks)}")
        try:
            await asyncio.gather(*tasks)
        except asyncio.CancelledError:
            logger.info("[red bold]cancelled by user.")
            if not self.sigexit.is_set():
                self.sigexit.set()
        finally:
            logger.info("[red bold]all mainlines exited, cleanup start.")
            for component_layer in reversed(resolve_requirements(set(self.launch_components.values()))):
                tasks = [
                    asyncio.create_task(component.cleanup(self), name=component.id)
                    for component in component_layer
                    if component.cleanup
                ]
                if tasks:
                    for task in tasks:
                        task.add_done_callback(lambda t: logger.info(f"{t.get_name()} cleanup finished."))
                    await asyncio.gather(*tasks)
            logger.info("[green bold]cleanup finished.")
            logger.warning("[red bold]exiting...")

    def launch_blocking(self):
        loop = asyncio.new_event_loop()
        self.sigexit = asyncio.Event(loop=loop)
        launch_task = loop.create_task(self.launch(), name="avilla-launch")
        try:
            loop.run_until_complete(launch_task)
        except KeyboardInterrupt:
            self.sigexit.set()
            launch_task.cancel()
            loop.run_until_complete(launch_task)
