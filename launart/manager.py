from __future__ import annotations

import asyncio
import contextlib
import contextvars
from itertools import chain
import signal
from contextvars import ContextVar
from functools import partial
from typing import TYPE_CHECKING, Any, Coroutine, ClassVar, Dict, Iterable, Optional, TypeVar, cast, overload

from loguru import logger

from launart._sideload import override
from launart.component import Service
from launart.status import ManagerStatus
from launart.utilles import (
    FlexibleTaskGroup,
    any_completed,
    cancel_alive_tasks,
    resolve_requirements,
)

TL = TypeVar("TL", bound=Service)


class Launart:
    components: Dict[str, Service]
    status: ManagerStatus
    tasks: dict[str, asyncio.Task]
    task_group: Optional[FlexibleTaskGroup] = None

    _context: ClassVar[ContextVar[Launart]] = ContextVar("launart._context")

    def __init__(self):
        self.components = {}
        self.tasks = {}
        self.status = ManagerStatus()

    @classmethod
    def current(cls) -> Launart:
        return cls._context.get()

    async def _sideload_tracker(self, component: Service) -> None:
        if TYPE_CHECKING:
            assert self.task_group is not None

        logger.info(f"Sideload {component.id}: injecting")

        local_status = ManagerStatus()
        shallow_self = cast(Launart, override(self, {"status": local_status}))
        component.manager = shallow_self

        task = asyncio.create_task(component.launch(shallow_self))
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

    async def _sideload_prepare(self, component: Service) -> None:
        if component.status.stage != "waiting-for-prepare":  # pragma: worst case
            logger.info(f"Waiting sideload {component.id} for prepare")
            await any_completed(
                self.tasks[component.id],
                component.status.wait_for("waiting-for-prepare"),
            )

        logger.info(f"Sideload {component.id}: preparing")

        component.status.stage = "preparing"
        await any_completed(
            self.tasks[component.id],
            component.status.wait_for("prepared"),
        )
        logger.info(f"Sideload {component.id}: preparation completed")

    async def _sideload_blocking(self, component: Service) -> None:
        logger.info(f"Sideload {component.id}: start blocking")

        await any_completed(
            self.tasks[component.id],
            component.status.wait_for("blocking-completed"),
        )
        logger.info(f"Sideload {component.id}: blocking completed")

    async def _sideload_cleanup(self, component: Service):
        if component.status.stage != "waiting-for-cleanup":  # pragma: worst case
            await any_completed(
                self.tasks[component.id],
                component.status.wait_for("waiting-for-cleanup"),
            )

        component.status.stage = "cleanup"

        await any_completed(
            self.tasks[component.id],
            component.status.wait_for("finished"),
        )
        logger.info(f"Sideload {component.id}: cleanup completed.")

    def _on_task_done(self, component: Service, t: asyncio.Task):
        try:
            exc = t.exception()
        except asyncio.CancelledError:
            logger.warning(
                f"[{component.id}] was cancelled in abort.",
                alt=f"[yellow bold]Component [magenta]{component.id}[/] was cancelled in abort.",
            )
            return
        if exc:
            logger.opt(exception=exc).error(
                f"[{component.id}] raised a exception.",
                alt=f"[red bold]Component [magenta]{component.id}[/] raised an exception.",
            )
            return

        if self.status.preparing:
            if "preparing" in component.stages:
                if component.status.prepared:
                    logger.info(f"Component {component.id} completed preparation.")
                else:
                    logger.error(f"Component {component.id} exited before preparation.")
        elif self.status.blocking:
            if "cleanup" in component.stages and component.status.stage != "finished":
                logger.warning(f"Component {component.id} exited without cleanup.")
            else:
                logger.success(f"Component {component.id} finished.")
        elif self.status.cleaning:
            if "cleanup" in component.stages:
                if component.status.finished:
                    logger.success(f"Component {component.id} finished.")
                else:
                    logger.warning(f"Component {component.id} exited before completing cleanup.")

        logger.info(
            f"Component {component.id} completed.",
            alt=rf"[green]Component [magenta]{component.id}[/magenta] completed.",
        )

    async def _component_prepare(self, task: asyncio.Task, component: Service):
        if component.status.stage != "waiting-for-prepare":  # pragma: worst case
            logger.info(f"Wait component {component.id} into preparing.")
            await any_completed(task, component.status.wait_for("waiting-for-prepare"))

        logger.info(f"Component {component.id} is preparing.")
        component.status.stage = "preparing"

        loop = asyncio.get_running_loop()
        listener_task = loop.create_task(component.status.wait_for("prepared"))
        done, pending = await any_completed(task, listener_task)
        if listener_task in pending:
            exc = task.exception()
            if exc is not None:
                task.result()

        logger.success(f"Component {component.id} is prepared.")

    async def _component_cleanup(self, task: asyncio.Task, component: Service):
        if component.status.stage != "waiting-for-cleanup":
            logger.info(f"Wait component {component.id} into cleanup.")
            await any_completed(task, component.status.wait_for("waiting-for-cleanup"))

        logger.info(f"Component {component.id} enter cleanup phase.")
        component.status.stage = "cleanup"

        await any_completed(task, component.status.wait_for("finished"))

    def add_component(self, component: Service):
        if self.task_group is not None:
            resolve_requirements([*self.components.values(), component])

        component.ensure_manager(self)

        if component.id in self.components:
            raise ValueError(f"Service {component.id} already exists.")

        if self.task_group is not None:
            tracker = asyncio.create_task(self._sideload_tracker(component))
            self.task_group.sideload_trackers[component.id] = tracker
            self.task_group.add(tracker)  # flush the waiter tasks

        self.components[component.id] = component

    @overload
    def get_component(self, target: type[TL]) -> TL:
        ...

    @overload
    def get_component(self, target: str) -> Service:
        ...

    def get_component(self, target: str | type[TL]) -> TL | Service:
        if isinstance(target, str):
            if target not in self.components:
                raise ValueError(f"Service {target} does not exists.")
            return self.components[target]

        if _id := getattr(target, "id", None):
            return self.get_component(_id)

        try:
            return next(comp for comp in self.components.values() if isinstance(comp, target))
        except StopIteration as e:
            raise ValueError(f"Service {target.__name__} does not exists.") from e

    def remove_component(
        self,
        component: str | Service,
    ):
        if isinstance(component, str):
            if component not in self.components:
                if self.task_group and component in self.task_group.sideload_trackers:
                    # sideload tracking, cannot gracefully remove (into exiting phase)
                    return
                raise ValueError(f"Service {component} does not exist.")
            target = self.components[component]
        else:
            if component not in self.components.values():
                raise ValueError(f"Service {component.id} does not exist.")

            target = component

        if self.task_group is None:
            del self.components[target.id]
            return

        resolve_requirements([service for service in self.components.values() if service.id != target.id])

        if target.id not in self.task_group.sideload_trackers:
            raise RuntimeError("Only sideload tasks can be removed at runtime!")

        tracker = self.task_group.sideload_trackers[target.id]
        if tracker.cancelled() or tracker.done():  # completed in silence, let it pass
            return

        if target.status.stage not in {"prepared", "blocking", "blocking-completed", "waiting-for-cleanup"}:
            raise RuntimeError(
                f"{target.id} obtains invalid stats to sideload active release, it's {target.status.stage}"
            )

        tracker.cancel()  # trigger cancel, and the tracker will start clean up

    async def _lifespan_finale(self, token: contextvars.Token):
        finale_tasks = [i for i in self.tasks.values() if not i.done()]
        if finale_tasks:
            await asyncio.wait(finale_tasks)

        self.task_group = None
        self._context.reset(token)
        self.status = ManagerStatus()

    async def _tasks_controler(self, tasks: list[Coroutine]):
        # 返回指示符。
        loop = asyncio.get_running_loop()
        done, pending = await asyncio.wait(map(loop.create_task, tasks), return_when=asyncio.FIRST_EXCEPTION)
        for i in done:
            if i.exception() is not None:
                return "exception-thrown", pending

        return "it-looks-good", done

    async def _fatal_cancel(self, token: contextvars.Token):
        for task_to_cancel in self.tasks.values():
            task_to_cancel.cancel()

        await self._lifespan_finale(token)
        return

    async def launch(self):
        if self.status.stage is not None:
            logger.error("Incorrect ownership, launart is already running.")
            return

        _token = self._context.set(self)

        loop = asyncio.get_running_loop()
        post = loop.create_task

        self.tasks = {}
        self.task_group = FlexibleTaskGroup()

        for _id, component in self.components.items():
            t = post(component.launch(self))
            t.add_done_callback(partial(self._on_task_done, component))
            self.tasks[_id] = t
            # self.task_group.add(self.tasks[k])
            # NOTE: 遗憾的, 我们仍然需要通过这种打洞的方式来实现, 而不是给每个 component 发一个保姆.

        self.status.stage = "preparing"

        try:
            prepared_tasks = []
            
            fatal_flag = False
            for components in resolve_requirements(self.components.values()):
                preparing_tasks = [
                    self._component_prepare(self.tasks[component.id], component)
                    for component in components
                    if "preparing" in component.stages
                ]
                if fatal_flag:
                    for component in components:
                        self.tasks[component.id].cancel()

                if preparing_tasks:
                    sym, tasks = await self._tasks_controler(preparing_tasks)
                    if sym == "exception-thrown":
                        for task_to_cancel in chain(tasks, prepared_tasks):
                            task_to_cancel.cancel()
                        fatal_flag = True

                    prepared_tasks.extend(tasks)

            if fatal_flag:
                await self._lifespan_finale(_token)
                return

        except asyncio.CancelledError:
            await self._fatal_cancel(_token)
            return

        self.status.stage = "blocking"

        blocking_tasks = [
            any_completed(self.tasks[component.id], component.status.wait_for("blocking-completed"))
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

            try:
                # cleanup the dangling sideload tasks first.
                if self.task_group.sideload_trackers:
                    for tracker in self.task_group.sideload_trackers.values():
                        tracker.cancel()
                    await asyncio.wait(self.task_group.sideload_trackers.values())

                self.status.stage = "cleaning"
                for idt, component in self.components.items():
                    if "cleanup" in component.stages and component.status.stage != "waiting-for-cleanup":
                        await any_completed(
                            self.tasks[idt],
                            component.status.wait_for("waiting-for-cleanup"),
                        )

                exceptional_tasks = []
                for components in resolve_requirements(self.components.values(), reverse=True):
                    cleanup_tasks = [
                        self._component_cleanup(self.tasks[component.id], component)
                        for component in components
                        if "cleanup" in component.stages
                    ]
                    if cleanup_tasks:
                        sym, tasks = await self._tasks_controler(cleanup_tasks)
                        if sym == "it-looks-good":
                            continue

                        exceptional_tasks.extend(exceptional_tasks)
            except asyncio.CancelledError:
                await self._fatal_cancel(_token)
                return

        self.status.stage = "finished"

        for task in exceptional_tasks:
            ...

        logger.success("Lifespan finished, waiting for finalization.", style="green bold")
        await self._lifespan_finale(_token)

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

        loop = loop or asyncio.get_event_loop()

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
            cancel_alive_tasks(loop)
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
