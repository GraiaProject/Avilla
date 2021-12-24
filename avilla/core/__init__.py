import asyncio
import importlib.metadata
from typing import (
    Any,
    Awaitable,
    Callable,
    Dict,
    Generic,
    Iterable,
    List,
    Set,
    Type,
)

from graia.broadcast import Broadcast
from graia.broadcast.interfaces.dispatcher import DispatcherInterface
from loguru import logger
from prompt_toolkit.patch_stdout import StdoutProxy
from rich.console import Console
from rich.logging import RichHandler
from rich.status import Status

from avilla.core.console import AvillaConsole
from avilla.core.event import MessageChainDispatcher, RelationshipDispatcher
from avilla.core.launch import LaunchComponent, resolve_requirements
from avilla.core.protocol import BaseProtocol
from avilla.core.service import Service, TInterface
from avilla.core.typing import T_Config, TExecutionMiddleware, T_Protocol
from avilla.core.utilles import as_async

AVILLA_ASCII_LOGO_AS_LIST = [
    "[bold]Avilla[/]: a universal asynchronous message flow solution, powered by [blue]Graia Project[/].",
    r"    _        _ _ _",
    r"   / \__   _(_) | | __ _",
    r"  / _ \ \ / / | | |/ _` |",
    r" / ___ \ V /| | | | (_| |",
    r"/_/   \_\_/ |_|_|_|\__,_|",
]

GRAIA_PROJECT_REPOS = ["avilla-core", "graia-broadcast"]


class RichStdoutProxy(StdoutProxy):
    "StdoutProxy with writelines support for Rich."

    def writelines(self, data: Iterable[str]) -> None:
        with self._lock:
            for d in data:
                self._write(d)


class Avilla(Generic[T_Protocol, T_Config]):
    broadcast: Broadcast
    configs: Dict[Type[T_Protocol], T_Config]
    launch_components: Dict[str, LaunchComponent]
    middlewares: List[TExecutionMiddleware]
    protocol: T_Protocol
    services: List[Service]
    sigexit: asyncio.Event

    enable_console: bool
    rich_console: Console

    def __init__(
        self,
        broadcast: Broadcast,
        protocol: Type[T_Protocol],
        services: List[Service],
        configs: Dict,
        middlewares: List[TExecutionMiddleware] = None,
        enable_console: bool = False
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
        if enable_console:
            import warnings
            warnings.warn("emm, you should not enable console in production, it's not stable and confusing.", Warning)
            self.rich_console = Console(file=RichStdoutProxy(raw=True))  # type: ignore
        else:
            self.rich_console = Console()

        self.broadcast.dispatcher_interface.inject_global_raw(
            RelationshipDispatcher(), MessageChainDispatcher()
        )

        @self.broadcast.dispatcher_interface.inject_global_raw
        async def _(interface: DispatcherInterface):
            if interface.annotation is Avilla:
                return self
            elif interface.annotation is protocol:
                return self.protocol

    def new_launch_component(
        self,
        id: str,
        mainline: Callable[["Avilla"], Awaitable[Any]],
        requirements: Set[str] = None,
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

    async def console_callback(self, command_or_str: str):
        # TODO: Commander Trigger
        pass

    async def launch(self):
        if self.enable_console:
            avilla_console = AvillaConsole(self.console_callback)
            self.launch_components["avilla.core.console"] = LaunchComponent(
                "avilla.core.console",
                set(),
                lambda _: avilla_console.start(),
                None,
                lambda _: as_async(avilla_console.stop)(),
            )

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

        try:
            await asyncio.gather(*[component.mainline(self) for component in self.launch_components.values()])
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
