from __future__ import annotations

from typing import TYPE_CHECKING, Any, Callable, Generic, Protocol, Type, TypeVar

from typing_extensions import Concatenate

from ..entity import BaseEntity
from ..globals import iter_layout
from ..typing import CR, AssignKeeper, Call, InP, OutP, P, R
from .compose import FnCompose
from .implement import FnImplementEntity, OverloadRecorder

if TYPE_CHECKING:
    from .record import FnRecord

K = TypeVar("K")

CCall = TypeVar("CCall", bound=Callable, covariant=True)
CCollect = TypeVar("CCollect", bound=Callable, covariant=True)


class ComposeShape(Protocol[CCollect, CCall]):
    @property
    def collect(self) -> CCollect:
        ...

    @property
    def call(self) -> CCall:
        ...


FnDef = Type[ComposeShape[Callable[InP, None], Callable[Concatenate["FnRecord", OutP], R]]]


class Fn(Generic[CCollect, CCall], BaseEntity):
    desc: FnCompose

    def __init__(self, compose: type[FnCompose]):
        self.desc = compose(self)

    @classmethod
    def declare(cls, desc: FnDef[InP, OutP, R]) -> Fn[Callable[InP, None], Callable[OutP, R]]:
        return cls(desc)  # type: ignore

    @property
    def impl(
        self: Fn[Callable[Concatenate[OverloadRecorder[CR], OutP], Any], Any],
    ) -> Callable[OutP, AssignKeeper[Call[..., CR]]]:
        def wrapper(*args: OutP.args, **kwargs: OutP.kwargs):
            def inner(impl: Callable[P, R] | FnImplementEntity[Callable[P, R]]):
                if not isinstance(impl, FnImplementEntity):
                    impl = FnImplementEntity(impl)

                impl.add_target(self, *args, **kwargs)
                return impl

            return inner

        return wrapper  # type: ignore

    def _call(self, *args, **kwargs):
        signature = self.desc.signature()

        for context in iter_layout(signature):
            if signature not in context.fn_implements:
                continue

            record = context.fn_implements[signature]
            return record.spec.desc.call(record, *args, **kwargs)
        else:
            raise NotImplementedError("cannot find any record with given fn declaration")

    @property
    def __call__(self) -> CCall:
        return self._call  # type: ignore
