import asyncio
from functools import partial
from typing import Any, Awaitable, Callable, Dict, List, Set, Type

from loguru import logger
from rich.console import Console
from rich.logging import RichHandler
from rich.status import Status

from avilla.core.launch import LaunchComponent, resolve_requirements
from avilla.core.service import Service, TInterface


class LaunchMock:
    launch_components: Dict[str, LaunchComponent]
    services: List[Service]

    rich_console: Console

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

        logger.info("[green bold]components prepared, switch to mainlines and block main thread.")

        loop = asyncio.get_running_loop()
        tasks = [
            loop.create_task(component.mainline(self))  # type: ignore
            for component in self.launch_components.values()
            if component.mainline
        ]
        for task, component_name in zip(tasks, self.launch_components.keys()):
            task.add_done_callback(
                partial(lambda n, t: logger.info(f"mainline {n} completed."), component_name)
            )
        try:
            logger.info(f"mainline count: {len(tasks)}")
            await asyncio.gather(*tasks)
        finally:
            logger.info("[red bold]mainlines exited, cleanup start.")
            for component_layer in reversed(resolve_requirements(set(self.launch_components.values()))):
                tasks = [
                    asyncio.create_task(component.cleanup(self), name=component.id)  # type: ignore
                    for component in component_layer
                    if component.cleanup
                ]
                if tasks:
                    for task in tasks:
                        task.add_done_callback(lambda t: logger.info(f"{t.get_name()} cleanup finished."))
                    await asyncio.wait(tasks)
            logger.info("[green bold]cleanup finished.")
            logger.warning("[red bold]exiting...")

    def launch_blocking(self):
        asyncio.get_event_loop().run_until_complete(self.launch())
