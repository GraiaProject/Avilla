from __future__ import annotations

import functools
from typing import Any, Callable

from .fn.implement import OverloadRecorder
from .context import CollectContext
from .globals import COLLECTING_CONTEXT_VAR, GLOBAL_COLLECT_CONTEXT, GLOBAL_INSTANCE_CONTEXT, INSTANCE_CONTEXT_VAR
from .typing import TYPE_CHECKING, AssignKeeperCls, P, R, TEntity

if TYPE_CHECKING:
    from typing_extensions import Concatenate

    from .fn.base import Call, Fn
    from .fn.implement import FnImplementEntity
    from .fn.record import FnImplement, FnRecord
    from .typing import CR, OutP


class scoped_collect(CollectContext):
    fn_implements: dict[FnImplement, FnRecord]
    _tocollect_list: dict[FnImplementEntity, None]
    finalize_cbs: list[Callable[[scoped_collect], Any]]
    cls: type | None = None

    def __init__(self) -> None:
        self.fn_implements = {}
        self.finalize_cbs = []
        self._tocollect_list = {}

    @classmethod
    def globals(cls):
        instance = cls()
        instance.fn_implements = GLOBAL_COLLECT_CONTEXT.fn_implements
        return instance

    @classmethod
    def env(cls):
        instance = cls()
        instance.fn_implements = COLLECTING_CONTEXT_VAR.get().fn_implements
        return instance

    def finalize(self):
        for cb in self.finalize_cbs:
            cb(self)

        for impl in self._tocollect_list:
            impl.collect(self)

    def on_collected(self, func: Callable[[scoped_collect], Any]):
        self.finalize_cbs.append(func)
        return func

    def remove_collected_callback(self, func: Callable[[scoped_collect], Any]):
        self.finalize_cbs.remove(func)
        return func

    @property
    def target(self):
        from .fn.implement import FnImplementEntity

        class LocalEndpoint:
            collector = self

            def __init_subclass__(cls, *, static: bool = False) -> None:
                self.cls = cls
                self.finalize()

                if static:
                    GLOBAL_INSTANCE_CONTEXT.instances[cls] = cls()

            @staticmethod
            def collect(entity: TEntity) -> TEntity:  # type: ignore
                return entity.collect(self)

            @staticmethod
            def ensure_self(func: Callable[Concatenate[Any, P], R]) -> Callable[P, R]:
                @functools.wraps(func)
                def wrapper(*args: P.args, **kwargs: P.kwargs) -> R:
                    assert self.cls is not None

                    instance = INSTANCE_CONTEXT_VAR.get().instances[self.cls]
                    return func(instance, *args, **kwargs)

                return wrapper

            @staticmethod
            def impl(
                fn: Fn[Callable[Concatenate[OverloadRecorder[CR], OutP], Any], Any], *args: OutP.args, **kwargs: OutP.kwargs
            ) -> AssignKeeperCls[Call[..., CR]]:
                def inner(impl: Callable[Concatenate[Any, P], R] | FnImplementEntity[Callable[P, R]]):
                    if not isinstance(impl, FnImplementEntity):
                        if not hasattr(impl, "__wrapped__"):
                            impl_call = LocalEndpoint.ensure_self(impl)
                        else:
                            impl_call: Callable[P, R] = impl  # type: ignore

                        impl = FnImplementEntity(impl_call)

                    impl.add_target(fn, *args, **kwargs)
                    self._tocollect_list[impl] = None
                    return impl

                return inner  # type: ignore

        return LocalEndpoint
