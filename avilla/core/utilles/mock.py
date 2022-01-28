import asyncio
from typing import (
    Any,
    Awaitable,
    Callable,
    Dict,
    Hashable,
    List,
    Optional,
    Set,
    Type,
    Union,
    cast,
)

from loguru import logger
from pydantic import BaseModel
from rich.console import Console
from rich.logging import RichHandler
from rich.status import Status

from avilla.core import Avilla
from avilla.core.config import (
    AvillaConfig,
    ConfigApplicant,
    ConfigFlushingMoment,
    ConfigProvider,
    TModel,
    direct,
)
from avilla.core.launch import LaunchComponent, resolve_requirements
from avilla.core.service import Service, TInterface


class LaunchMock:
    launch_components: Dict[str, LaunchComponent]
    services: List[Service]

    rich_console: Console
    sigexit: asyncio.Event

    def __init__(self, launch_components: Dict[str, LaunchComponent], services: List[Service]):
        self.launch_components = {
            **launch_components,
            **{i.launch_component.id: i.launch_component for i in services},
        }
        self.services = services
        self.rich_console = Console()

    def new_launch_component(
        self,
        id: str,
        requirements: Set[str] = None,
        mainline: Callable[["LaunchMock"], Awaitable[Any]] = None,
        prepare: Callable[["LaunchMock"], Awaitable[Any]] = None,
        cleanup: Callable[["LaunchMock"], Awaitable[Any]] = None,
    ) -> LaunchComponent:
        component = LaunchComponent(id, requirements or set(), mainline, prepare, cleanup)  # type: ignore
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

        for service in self.services:
            logger.info(f"using service: {service.__class__.__name__}")

        logger.info(f"launch components count: {len(self.launch_components)}")

        with Status("[orange bold]preparing components...", console=self.rich_console) as status:
            for component_layer in resolve_requirements(set(self.launch_components.values())):
                tasks = [
                    asyncio.create_task(component.prepare(self), name=component.id)  # type: ignore
                    for component in component_layer
                    if component.prepare
                ]
                if tasks:
                    for task in tasks:
                        task.add_done_callback(lambda t: status.update(f"{t.get_name()} prepared."))
                    await asyncio.wait(tasks)
            status.update("all launch components prepared.")
            await asyncio.sleep(1)

        logger.info("[green bold]components prepared, switch to mainlines and block main thread.")

        loop = asyncio.get_running_loop()
        tasks = [
            loop.create_task(component.mainline(self), name=component.id)  # type: ignore
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
                    asyncio.create_task(component.cleanup(self), name=component.id)  # type: ignore
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


class ConfigMock:
    config: Dict[Union[ConfigApplicant, Type[ConfigApplicant]], Dict[Hashable, "ConfigProvider[BaseModel]"]]

    def __init__(
        self,
        config: Dict[
            Union[ConfigApplicant[TModel], Type[ConfigApplicant[TModel]]],
            Union[TModel, "ConfigProvider[TModel]", Dict[Hashable, Union[TModel, "ConfigProvider[TModel]"]]],
        ],
    ):
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

    def get_config(
        self, applicant: Union[ConfigApplicant[TModel], Type[ConfigApplicant[TModel]]], scope: Hashable = ...
    ) -> Optional[TModel]:
        scoped = cast(Dict[Hashable, "ConfigProvider[TModel]"], self.config.get(applicant))
        if scoped:
            provider = scoped.get(scope)
            if provider:
                return provider.get_config()

    async def flush_config(self, when: ConfigFlushingMoment):
        for applicant, scoped in self.config.items():
            if when not in applicant.init_moment.values():
                continue
            for scope, provider in scoped.items():
                await provider.provide(self, applicant.config_model, scope)  # type: ignore
