import asyncio
import importlib.metadata
from contextlib import asynccontextmanager
from typing import (
    Any,
    Awaitable,
    Callable,
    Dict,
    Generic,
    Hashable,
    List,
    Optional,
    Set,
    Tuple,
    Type,
    Union,
    cast,
)

from graia.broadcast import Broadcast
from graia.broadcast.entities.dispatcher import BaseDispatcher
from graia.broadcast.interfaces.dispatcher import DispatcherInterface
from loguru import logger
from pydantic import BaseModel
from rich.console import Console
from rich.logging import RichHandler
from rich.status import Status

from avilla.core.config import (
    AvillaConfig,
    ConfigApplicant,
    ConfigFlushingMoment,
    ConfigProvider,
    TModel,
    direct,
)
from avilla.core.context import ctx_avilla
from avilla.core.event import RelationshipDispatcher
from avilla.core.launch import LaunchComponent, resolve_requirements
from avilla.core.protocol import BaseProtocol
from avilla.core.resource import ResourceProvider
from avilla.core.selectors import resource as resource_selector
from avilla.core.service import Service, TInterface
from avilla.core.service.entity import ExportInterface
from avilla.core.stream import Stream
from avilla.core.typing import TExecutionMiddleware
from avilla.core.utilles import DeferDispatcher, priority_strategy
from avilla.io.core.memcache import MemcacheService

AVILLA_ASCII_LOGO_AS_LIST = [
    "[bold]Avilla[/]: a universal asynchronous message flow solution, powered by [blue]Graia Project[/].",
    r"    _        _ _ _",
    r"   / \__   _(_) | | __ _",
    r"  / _ \ \ / / | | |/ _` |",
    r" / ___ \ V /| | | | (_| |",
    r"/_/   \_\_/ |_|_|_|\__,_|",
]

GRAIA_PROJECT_REPOS = ["avilla-core", "graia-broadcast", "graia-saya", "graia-scheduler"]


class Avilla(ConfigApplicant[AvillaConfig]):
    broadcast: Broadcast
    protocols: List[BaseProtocol]
    protocol_classes: List[Type[BaseProtocol]]

    launch_components: Dict[str, LaunchComponent]
    middlewares: List[TExecutionMiddleware]
    services: List[Service]
    resource_providers: List[ResourceProvider]
    config: Dict[Union[ConfigApplicant, Type[ConfigApplicant]], Dict[Hashable, "ConfigProvider[BaseModel]"]]

    _service_interfaces: Dict[Type[ExportInterface], Service]
    _res_provider_types: Dict[str, ResourceProvider]

    sigexit: asyncio.Event
    maintask: Optional[asyncio.Task] = None
    rich_console: Console

    init_moment = {AvillaConfig: ConfigFlushingMoment.before_prepare}
    config_model = AvillaConfig

    def __init__(
        self,
        broadcast: Broadcast,
        protocols: List[Type[BaseProtocol]],
        services: List[Service],
        config: Dict[
            Union[ConfigApplicant[TModel], Type[ConfigApplicant[TModel]]],
            Union[TModel, "ConfigProvider[TModel]", Dict[Hashable, Union[TModel, "ConfigProvider[TModel]"]]],
        ],
        middlewares: List[TExecutionMiddleware] = None,
    ):
        self.broadcast = broadcast
        self.protocol_classes = protocols
        self.sigexit = asyncio.Event(loop=broadcast.loop)
        self.resource_providers = []
        self.launch_components = {}
        self._flush_resprov_map()
        self.middlewares = middlewares or []
        self.services = services
        self._flush_serif_map()
        self.protocols = [protocol(self) for protocol in protocols]
        self._protocol_map = dict(zip(protocols, self.protocols))
        self.launch_components.update(
            {
                **({i.launch_component.id: i.launch_component for i in services}),
                **({protocol.launch_component.id: protocol.launch_component for protocol in self.protocols}),
            }
        )
        self.rich_console = Console()

        for protocol in self.protocols:
            if isinstance(protocol, ResourceProvider):  # Protocol 可以作为资源提供方
                self.resource_providers.append(protocol)

        self.broadcast.finale_dispatchers.append(RelationshipDispatcher())

        @self.broadcast.finale_dispatchers.append
        class AvillaBuiltinDispatcher(BaseDispatcher):
            @staticmethod
            async def catch(interface: DispatcherInterface):
                if interface.annotation is Avilla:
                    return self
                elif interface.annotation in self._protocol_map:
                    return self._protocol_map[interface.annotation]

        # config shortcut flatten

        self.config = {}
        for applicant, target_conf in config.items():
            if not isinstance(target_conf, dict):
                target_conf = {...: target_conf}

            for scope, shortcut in target_conf.items():
                if not isinstance(shortcut, ConfigProvider):
                    if isinstance(shortcut, BaseModel):
                        target_conf[scope] = direct(shortcut)  # type: ignore
                    else:
                        raise ValueError(f"invalid configuration: {shortcut}")

            self.config[applicant] = target_conf  # type: ignore
        self.config.setdefault(Avilla, {...: direct(AvillaConfig())})  # type: ignore
        # all use default value.

        # builtin settings
        avilla_config = cast(AvillaConfig, self.get_config(Avilla))
        if avilla_config.enable_builtin_services:
            if avilla_config.use_memcache:
                self.add_service(MemcacheService())
        if avilla_config.use_defer:
            self.broadcast.finale_dispatchers.append(DeferDispatcher())
        if avilla_config.enable_builtin_resource_providers:
            if avilla_config.use_localfile:
                from avilla.core.utilles.resource import LocalFileResourceProvider

                self.resource_providers.append(LocalFileResourceProvider())
                self._flush_resprov_map()

    def has_service(self, service_type: Type[Service]) -> bool:
        for service in self.services:
            if isinstance(service, service_type):
                return True
        return False

    def get_service(self, service_type: Type[Service]) -> Service:
        for service in self.services:
            if isinstance(service, service_type):
                return service
        raise ValueError(f"service not found: {service_type}")

    def get_config(
        self, applicant: Union[ConfigApplicant[TModel], Type[ConfigApplicant[TModel]]], scope: Hashable = ...
    ) -> Optional[TModel]:
        scoped = cast(Dict[Hashable, "ConfigProvider[TModel]"], self.config.get(applicant))
        if scoped:
            provider = scoped.get(scope)
            if provider:
                return provider.get_config()

    def get_config_scopes(self, applicant: Union[ConfigApplicant[TModel], Type[ConfigApplicant[TModel]]]):
        scoped = self.config.get(applicant)
        if scoped:
            return scoped.keys()

    def _flush_resprov_map(self):
        self._res_provider_types = priority_strategy(
            self.resource_providers, lambda p: p.supported_resource_types  # type: ignore
        )

    def _flush_serif_map(self):
        self._service_interfaces = priority_strategy(self.services, lambda s: s.supported_interface_types)

    async def flush_config(self, when: ConfigFlushingMoment):
        for applicant, scoped in self.config.items():
            if when not in applicant.init_moment.values():
                continue
            for scope, provider in scoped.items():
                await provider.provide(self, applicant.config_model, scope)

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
        self._flush_serif_map()
        if isinstance(service, ResourceProvider):
            self.resource_providers.append(service)
            self._flush_resprov_map()
        launch_component = service.launch_component
        self.launch_components[launch_component.id] = launch_component

    def remove_service(self, service: Service):
        if service not in self.services:
            raise ValueError("service doesn't exist.")
        self.services.remove(service)
        if isinstance(service, ResourceProvider):
            self.resource_providers.remove(service)
            self._flush_resprov_map()
        del self.launch_components[service.launch_component.id]

    def get_interface(self, interface_type: Type[TInterface]) -> TInterface:
        if interface_type not in self._service_interfaces:
            raise ValueError(f"interface type {interface_type} not supported.")
        return self._service_interfaces[interface_type].get_interface(interface_type)

    @asynccontextmanager
    async def access_resource(self, resource: resource_selector):
        resource_type = list(resource.path.keys())[0]
        if "provider" in resource.path:
            provider = resource.path["provider"]
        else:
            if resource_type not in self._res_provider_types:
                raise ValueError(f"resource type {resource_type} not supported.")
            provider = self._res_provider_types[resource_type]
        async with provider.access_resource(resource) as accessor:
            yield accessor

    async def fetch_resource(self, resource: resource_selector):
        async with self.access_resource(resource) as accessor:
            return await accessor.read()

    @asynccontextmanager
    async def get_resource_meta(self, resource: resource_selector):
        async with self.access_resource(resource) as accessor:
            yield await accessor.meta()

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

        logger.info("start config flushing, stage: before_prepare")
        await self.flush_config(ConfigFlushingMoment.before_prepare)

        with Status("[orange bold]preparing components...", console=self.rich_console) as status:
            for component_layer in resolve_requirements(set(self.launch_components.values())):
                tasks = [
                    asyncio.create_task(component.prepare(self), name=component.id)
                    for component in component_layer
                    if component.prepare
                ]
                logger.debug(tasks)
                for task in tasks:
                    task.add_done_callback(lambda t: status.update(f"{t.get_name()} prepared."))
                if tasks:
                    await asyncio.wait(tasks)
            status.update("all launch components prepared.")
            await asyncio.sleep(1)

        logger.info("start config flushing, stage: before_mainline")
        await self.flush_config(ConfigFlushingMoment.before_mainline)

        logger.info("[green bold]components prepared, switch to mainlines and block main thread.")

        async def config_flushing_in_mainline(_):
            # wait for all components prepared
            # because we can not know whether the components are pending while they prepared their work,
            # so we don't recommend to use in_mainline moment to flush config.
            # and we are thinking for sometime to remove this moment...
            await asyncio.sleep(1)
            await self.flush_config(ConfigFlushingMoment.in_mainline)

        self.new_launch_component("avilla.core.config_flush.mainline", mainline=config_flushing_in_mainline)

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
            if tasks:
                self.maintask = loop.create_task(asyncio.wait(tasks))
                await asyncio.shield(self.maintask)
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
