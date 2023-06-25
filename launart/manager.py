from __future__ import annotations

import asyncio
import contextlib
import signal
from contextvars import ContextVar
from functools import partial
from typing import (
    TYPE_CHECKING,
    Any,
    ClassVar,
    Dict,
    Iterable,
    Literal,
    Optional,
    Type,
    TypeVar,
    cast,
)

from loguru import logger
from statv import Stats, Statv

from launart._sideload import FutureMark, override
from launart.component import Launchable, resolve_requirements
from launart.service import ExportInterface, Service
from launart.utilles import FlexibleTaskGroup, priority_strategy

U_ManagerStage = Literal["preparing", "blocking", "cleaning", "finished"]
E = TypeVar("E", bound=ExportInterface)


class ManagerStatus(Statv):
    stage = Stats[Optional[U_ManagerStage]]("U_ManagerStage", default=None)
    exiting = Stats[bool]("exiting", default=False)

    def __init__(self) -> None:
        super().__init__()

    def __repr__(self) -> str:
        return f"<ManagerStatus stage={self.stage} waiters={len(self._waiters)}>"

    @property
    def preparing(self) -> bool:
        return self.stage == "preparing"

    @property
    def blocking(self) -> bool:
        return self.stage == "blocking"

    @property
    def cleaning(self) -> bool:
        return self.stage == "cleaning"

    async def wait_for_update(self, *, current: str | None = None, stage: U_ManagerStage | None = None):
        waiter = asyncio.Future()
        if current is not None:
            waiter.add_done_callback(FutureMark(current, stage))
        self._waiters.append(waiter)
        try:
            return await waiter
        finally:
            self._waiters.remove(waiter)

    async def wait_for_preparing(self):
        while not self.preparing:
            await self.wait_for_update()

    async def wait_for_blocking(self):
        while not self.blocking:
            await self.wait_for_update()

    async def wait_for_cleaning(self, *, current: str | None = None):
        while not self.cleaning:
            await self.wait_for_update(current=current, stage="cleaning")

    async def wait_for_finished(self, *, current: str | None = None):
        while self.stage not in {"finished", None}:
            await self.wait_for_update(current=current, stage="finished")

    async def wait_for_sigexit(self):
        while self.stage in {"preparing", "blocking"} and not self.exiting:
            await self.wait_for_update()


class Launart:
    components: Dict[str, Launchable]
    status: ManagerStatus
    tasks: dict[str, asyncio.Task]
    task_group: Optional[FlexibleTaskGroup] = None

    _service_bind: Dict[Type[ExportInterface], Service]

    _context: ClassVar[ContextVar[Launart]] = ContextVar("launart._context")
    _priority_overrides: Dict[Type[ExportInterface], Service]

    def __init__(self):
        self.components = {}
        self._service_bind = {}
        self.status = ManagerStatus()
        self.tasks = {}
        self._priority_overrides = {}

    @classmethod
    def current(cls) -> Launart:
        return cls._context.get()

    def add_component(self, component: Launchable):
        component.ensure_manager(self)
        if component.id in self.components:
            raise ValueError(f"Launchable {component.id} already exists.")
        if self.task_group is not None:
            component._required_id  # Evaluate requirements automatically.
            tracker = asyncio.create_task(self._sideload_tracker(component))
            self.task_group.sideload_trackers[component.id] = tracker
            self.task_group.add(tracker)  # flush the waiter tasks
        self.components[component.id] = component
        if isinstance(component, Service):
            self._update_service_bind()

    def get_component(self, id: str) -> Launchable:
        if id not in self.components:
            raise ValueError(f"Launchable {id} does not exists.")
        return self.components[id]

    def get_service(self, id: str) -> Service:
        component = self.get_component(id)
        if not isinstance(component, Service):
            raise TypeError(f"{id} is not a service.")
        return component

    def override_bind(self, interface: type[ExportInterface], service: Service) -> None:
        if interface in self._priority_overrides:
            raise ValueError(f"{interface} is already overridden by {self._priority_overrides[interface]}")
        self._priority_overrides[interface] = service
        self._service_bind.update(self._priority_overrides)

    def remove_component(
        self,
        component: str | Launchable,
    ):
        if isinstance(component, str):
            if component not in self.components:
                if self.task_group and component in self.task_group.sideload_trackers:
                    # sideload tracking, cannot gracefully remove (into exiting phase)
                    return
                raise ValueError(f"Launchable {id} does not exist.")
            target = self.components[component]
        else:
            target = component
        if self.task_group is None:
            del self.components[target.id]
        else:
            if target.id not in self.task_group.sideload_trackers:
                raise RuntimeError("Only sideload tasks can be removed at runtime!")
            tracker = self.task_group.sideload_trackers[target.id]
            if tracker.cancelled() or tracker.done():  # completed in silence, let it pass
                return
            if target.status.stage not in {"prepared", "blocking", "blocking-completed", "waiting-for-cleanup"}:
                raise RuntimeError(
                    f"{target.id} obtains invalid stats to sideload active release, it's {target.status.stage}"
                )
            tracker.cancel()  # trigger cancel, and the tracker will start clean up the
        if isinstance(target, Service):
            self._update_service_bind()

    def _update_service_bind(self):
        self._service_bind = priority_strategy(
            [i for i in self.components.values() if isinstance(i, Service)],
            lambda a: a.supported_interface_types,
        )
        self._service_bind.update(self._priority_overrides)

    async def _sideload_tracker(self, component: Launchable) -> None:
        if TYPE_CHECKING:
            assert self.task_group is not None

        logger.info(f"Sideload {component.id}: injecting")

        local_status = ManagerStatus()
        shallow_self = cast(Launart, override(self, {"status": local_status}))
        component.manager = shallow_self

        task = asyncio.create_task(component.launch(shallow_self), name=component.id)
        task.add_done_callback(partial(self._on_task_done, component))
        self.tasks[component.id] = task

        local_status.stage = "preparing"
        if "preparing" in component.stages:
            await self._sideload_prepare(component)

        with contextlib.suppress(asyncio.CancelledError):
            local_status.stage = "blocking"
            if "blocking" in component.stages:
                await self._sideload_blocking(component)

        local_status.update_multi(
            {
                ManagerStatus.stage: "cleaning",
                ManagerStatus.exiting: True,
            }
        )
        if "cleanup" in component.stages:
            await self._sideload_cleanup(component)

        if not task.done() or not task.cancelled():  # pragma: worst case
            await task
        logger.info(f"Sideload {component.id}: completed.")
        del self.tasks[component.id]
        del self.components[component.id]
        del self.task_group.sideload_trackers[component.id]

    async def _sideload_prepare(self, component: Launchable) -> None:
        if component.status.stage != "waiting-for-prepare":  # pragma: worst case
            logger.info(f"Waiting sideload {component.id} for prepare")
            await asyncio.wait(
                [
                    self.tasks[component.id],
                    asyncio.create_task(component.status.wait_for("waiting-for-prepare")),
                ],
                return_when=asyncio.FIRST_COMPLETED,
            )

        logger.info(f"Sideload {component.id}: preparing")

        component.status.stage = "preparing"
        await asyncio.wait(
            [
                self.tasks[component.id],
                asyncio.create_task(component.status.wait_for("prepared")),
            ],
            return_when=asyncio.FIRST_COMPLETED,
        )
        logger.info(f"Sideload {component.id}: preparation completed")

    async def _sideload_blocking(self, component: Launchable) -> None:
        logger.info(f"Sideload {component.id}: start blocking")

        await asyncio.wait(
            [
                self.tasks[component.id],
                asyncio.create_task(component.status.wait_for("blocking-completed")),
            ],
            return_when=asyncio.FIRST_COMPLETED,
        )
        logger.info(f"Sideload {component.id}: blocking completed")

    async def _sideload_cleanup(self, component: Launchable):
        if component.status.stage != "waiting-for-cleanup":  # pragma: worst case
            await asyncio.wait(
                [
                    self.tasks[component.id],
                    asyncio.create_task(component.status.wait_for("waiting-for-cleanup")),
                ],
                return_when=asyncio.FIRST_COMPLETED,
            )

        component.status.stage = "cleanup"

        await asyncio.wait(
            [
                self.tasks[component.id],
                asyncio.create_task(component.status.wait_for("finished")),
            ],
            return_when=asyncio.FIRST_COMPLETED,
        )
        logger.info(f"Sideload {component.id}: cleanup completed.")

    def _on_task_done(self, component: Launchable, t: asyncio.Task):
        try:
            exc = t.exception()
        except asyncio.CancelledError:
            logger.warning(
                f"[{t.get_name()}] was cancelled in abort.",
                alt=f"[yellow bold]component [magenta]{t.get_name()}[/] was cancelled in abort.",
            )
            return
        if exc:
            logger.opt(exception=exc).error(
                f"[{t.get_name()}] raised a exception.",
                alt=f"[red bold]component [magenta]{t.get_name()}[/] raised an exception.",
            )
            return

        if self.status.preparing:
            if "preparing" in component.stages:
                if component.status.prepared:
                    logger.info(f"Component {t.get_name()} completed preparation.")
                else:
                    logger.error(f"Component {t.get_name()} exited before preparation.")
        elif self.status.blocking:
            if "cleanup" in component.stages and component.status.stage != "finished":
                logger.warning(f"Component {t.get_name()} exited without cleanup.")
            else:
                logger.success(f"Component {t.get_name()} finished.")
        elif self.status.cleaning:
            if "cleanup" in component.stages:
                if component.status.finished:
                    logger.success(f"component {t.get_name()} finished.")
                else:
                    logger.warning(f"component {t.get_name()} exited before completing cleanup.")

        logger.info(
            f"[{t.get_name()}] completed.",
            alt=rf"[green]\[[magenta]{t.get_name()}[/magenta]] completed.",
        )

    async def _component_prepare(self, task: asyncio.Task, component: Launchable):
        if component.status.stage != "waiting-for-prepare":  # pragma: worst case
            logger.info(f"wait component {component.id} into preparing.")
            await asyncio.wait(
                [
                    task,
                    asyncio.create_task(component.status.wait_for("waiting-for-prepare")),
                ],
                return_when=asyncio.FIRST_COMPLETED,
            )

        logger.info(f"component {component.id} is preparing.")
        component.status.stage = "preparing"

        await asyncio.wait(
            [
                task,
                asyncio.create_task(component.status.wait_for("prepared")),
            ],
            return_when=asyncio.FIRST_COMPLETED,
        )
        logger.success(f"component {component.id} is prepared.")

    async def _component_cleanup(self, task: asyncio.Task, component: Launchable):
        if component.status.stage != "waiting-for-cleanup":
            logger.info(f"Wait component {component.id} into cleanup.")
            await asyncio.wait(
                [
                    task,
                    asyncio.create_task(component.status.wait_for("waiting-for-cleanup")),
                ],
                return_when=asyncio.FIRST_COMPLETED,
            )

        logger.info(f"Component {component.id} enter cleanup phase.")
        component.status.stage = "cleanup"

        await asyncio.wait(
            [
                task,
                asyncio.create_task(component.status.wait_for("finished")),
            ],
            return_when=asyncio.FIRST_COMPLETED,
        )

    async def launch(self):
        _token = self._context.set(self)
        if self.status.stage is not None:
            logger.error("Incorrect ownership, launart is already running.")
            return
        self.tasks = {}
        loop = asyncio.get_running_loop()
        self.task_group = FlexibleTaskGroup()
        into = loop.create_task

        for k, v in self.components.items():
            t = into(v.launch(self), name=f"launch#{k}")
            t.add_done_callback(partial(self._on_task_done, v))  # NOTE
            self.tasks[k] = t
            #self.task_group.add(self.tasks[k])  # NOTE

        self.status.stage = "preparing"

        for components in resolve_requirements(self.components.values()):
            preparing_tasks = [
                self._component_prepare(self.tasks[component.id], component)
                for component in components
                if "preparing" in component.stages
            ]
            if preparing_tasks:
                await asyncio.gather(*preparing_tasks)

        self.status.stage = "blocking"

        blocking_tasks = [
            asyncio.wait(
                [
                    self.tasks[component.id],
                    into(component.status.wait_for("blocking-completed")),
                ],
                return_when=asyncio.FIRST_COMPLETED,
            )
            for component in self.components.values()
            if "blocking" in component.stages
        ]

        try:
            if blocking_tasks:
                self.task_group.add(*blocking_tasks)
                await self.task_group
        finally:
            self.status.exiting = True

            logger.info("Entering cleanup phase.", style="yellow bold")
            # cleanup the dangling sideload tasks first.
            if self.task_group.sideload_trackers:
                for tracker in self.task_group.sideload_trackers.values():
                    tracker.cancel()
                await asyncio.wait(self.task_group.sideload_trackers.values())

            self.status.stage = "cleaning"

            for components in resolve_requirements(self.components.values(), reverse=True):
                cleanup_tasks = [
                    self._component_cleanup(self.tasks[component.id], component)
                    for component in components
                    if "cleanup" in component.stages
                ]
                if cleanup_tasks:
                    await asyncio.gather(*cleanup_tasks)

        self.status.stage = "finished"
        logger.success("Lifespan finished, waiting for finalization.", style="green bold")

        finale_tasks = [i for i in self.tasks.values() if not i.done()]
        if finale_tasks:
            await asyncio.wait(finale_tasks)

        self.task_group = None
        self._context.reset(_token)

        logger.success("Launart finished.", style="green bold")

    def launch_blocking(
        self,
        *,
        loop: Optional[asyncio.AbstractEventLoop] = None,
        stop_signal: Iterable[signal.Signals] = (signal.SIGINT,),
    ):
        import contextlib
        import functools
        import threading

        loop = loop or asyncio.new_event_loop()

        launch_task = loop.create_task(self.launch(), name="amnesia-launch")
        handled_signals: Dict[signal.Signals, Any] = {}
        signal_handler = functools.partial(self._on_sys_signal, main_task=launch_task)
        if threading.current_thread() is threading.main_thread():  # pragma: worst case
            try:
                for sig in stop_signal:
                    handled_signals[sig] = signal.getsignal(sig)
                    signal.signal(sig, signal_handler)
            except ValueError:  # pragma: no cover
                # `signal.signal` may throw if `threading.main_thread` does
                # not support signals
                handled_signals.clear()

        loop.run_until_complete(launch_task)

        for sig, handler in handled_signals.items():
            if signal.getsignal(sig) is signal_handler:
                signal.signal(sig, handler)

        try:
            self._cancel_tasks(loop)
            loop.run_until_complete(loop.shutdown_asyncgens())
            with contextlib.suppress(RuntimeError, AttributeError):
                # LINK: https://docs.python.org/3.10/library/asyncio-eventloop.html#asyncio.loop.shutdown_default_executor
                loop.run_until_complete(loop.shutdown_default_executor())
        finally:
            logger.success("Lifespan completed.", style="green bold")

    def _on_sys_signal(self, _, __, main_task: asyncio.Task):
        self.status.exiting = True
        if self.task_group is not None:
            self.task_group.stop = True
            if self.task_group.blocking_task is not None:  # pragma: worst case
                self.task_group.blocking_task.cancel()
        if not main_task.done():
            main_task.cancel()
            # wakeup loop if it is blocked by select() with long timeout
            main_task._loop.call_soon_threadsafe(lambda: None)
            logger.warning("Ctrl-C triggered by user.", style="dark_orange bold")

    @staticmethod
    def _cancel_tasks(loop: asyncio.AbstractEventLoop):
        import asyncio
        import asyncio.tasks

        to_cancel = asyncio.tasks.all_tasks(loop)
        if to_cancel:
            for tsk in to_cancel:
                tsk.cancel()
            loop.run_until_complete(asyncio.gather(*to_cancel, return_exceptions=True))

            for task in to_cancel:  # pragma: no cover
                # BELIEVE IN PSF
                if task.cancelled():
                    continue
                if task.exception() is not None:
                    logger.opt(exception=task.exception()).error(f"Unhandled exception when shutting down {task}:")
