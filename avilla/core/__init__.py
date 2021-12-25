import asyncio
import importlib.metadata
from functools import partial
from typing import (
    Any,
    Awaitable,
    Callable,
    Dict,
    Generic,
    List,
    Optional,
    Set,
    Type,
)

from graia.broadcast import Broadcast
from graia.broadcast.interfaces.dispatcher import DispatcherInterface
from loguru import logger
from rich.console import Console
from rich.logging import RichHandler
from rich.status import Status

from avilla.core.context import ctx_avilla
from avilla.core.event import RelationshipDispatcher
from avilla.core.launch import LaunchComponent, resolve_requirements
from avilla.core.protocol import BaseProtocol
from avilla.core.service import Service, TInterface
from avilla.core.typing import TConfig, TExecutionMiddleware, TProtocol

AVILLA_ASCII_LOGO_AS_LIST = [
    "[bold]Avilla[/]: a universal asynchronous message flow solution, powered by [blue]Graia Project[/].",
    r"    _        _ _ _",
    r"   / \__   _(_) | | __ _",
    r"  / _ \ \ / / | | |/ _` |",
    r" / ___ \ V /| | | | (_| |",
    r"/_/   \_\_/ |_|_|_|\__,_|",
]

GRAIA_PROJECT_REPOS = ["avilla-core", "graia-broadcast"]


class Avilla(Generic[TProtocol, TConfig]):
    broadcast: Broadcast
    configs: Dict[Type[TProtocol], TConfig]
    launch_components: Dict[str, LaunchComponent]
    middlewares: List[TExecutionMiddleware]
    protocol: TProtocol
    services: List[Service]
    sigexit: asyncio.Event

    rich_console: Console

    def __init__(
        self,
        broadcast: Broadcast,
        protocol: Type[TProtocol],
        services: List[Service],
        configs: Dict,
        middlewares: List[TExecutionMiddleware] = None,
    ):
        self.broadcast = broadcast
        self.protocol = protocol(self, configs.get(protocol))
        self.configs = configs
        self.services = services
        self.middlewares = middlewares or []
        self.launch_components = {
            **({i.launch_component.id: i.launch_component for i in services}),
            self.protocol.launch_component.id: self.protocol.launch_component,
        }
        self.sigexit = asyncio.Event()
        self.rich_console = Console()

        self.broadcast.dispatcher_interface.inject_global_raw(RelationshipDispatcher())

        @self.broadcast.dispatcher_interface.inject_global_raw
        async def _(interface: DispatcherInterface):
            if interface.annotation is Avilla:
                return self
            elif interface.annotation is protocol:
                return self.protocol

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
        launch_component = service.launch_component
        self.launch_components[launch_component.id] = launch_component

    def remove_service(self, service: Service):
        if service not in self.services:
            raise ValueError("service doesn't exist.")
        self.services.remove(service)
        del self.launch_components[service.launch_component.id]

    def get_interface(self, interface_type: Type[TInterface]) -> TInterface:
        for service in self.services:
            if interface_type in service.supported_interface_types:
                return service.get_interface(interface_type)
        raise ValueError(f"interface type {interface_type} not supported.")

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

        if self.protocol.__class__.platform is not BaseProtocol.platform:
            logger.info(f"using platform: {self.protocol.__class__.platform.universal_identifier}")

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

        logger.info("[green bold]components prepared, switch to mainlines and block main thread.")

        loop = asyncio.get_running_loop()
        tasks = [
            loop.create_task(component.mainline(self))
            for component in self.launch_components.values()
            if component.mainline
        ]
        for task, component_name in zip(tasks, self.launch_components.keys()):
            task.add_done_callback(
                partial(lambda n, t: logger.info(f"mainline {n} completed."), component_name)
            )
        try:
            await asyncio.gather(*tasks)
        finally:
            self.sigexit.set()
            logger.info("[red bold]mainlines exited, cleanup start.")
            for component_layer in reversed(resolve_requirements(set(self.launch_components.values()))):
                tasks = [
                    asyncio.create_task(component.cleanup(self), name=component.id)
                    for component in component_layer
                    if component.cleanup
                ]
                for task in tasks:
                    task.add_done_callback(lambda t: logger.info(f"{t.get_name()} cleanup finished."))
                await asyncio.wait(tasks)
            logger.info("[green bold]cleanup finished.")
            logger.warning("[red bold]exiting...")

    def launch_blocking(self):
        asyncio.get_event_loop().run_until_complete(self.launch())
