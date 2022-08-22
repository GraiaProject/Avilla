from __future__ import annotations

from typing import (
    TYPE_CHECKING,
    Any,
    Awaitable,
    Callable,
    Concatenate,
    Generic,
    ParamSpec,
    TypeVar,
    overload,
)

from typing_extensions import Unpack

from avilla.core.traitof import TargetTraitCall
from avilla.core.traitof.recorder import Recorder
from avilla.core.traitof.signature import CompleteRule, EventKeyGetter
from avilla.core.traitof.signature import Impl as _Impl
from avilla.core.traitof.signature import ImplDefaultTarget
from avilla.core.traitof.signature import Pull as _Pull
from avilla.core.traitof.signature import ResourceFetch as _ResourceFatch
from avilla.core.utilles.selector import Selector

from .context import eval_dotpath, get_current_namespace, ctx_prefix

if TYPE_CHECKING:
    from avilla.core.cell import Cell, CellOf
    from avilla.core.relationship import Relationship

    from . import TraitCall

_P = ParamSpec("_P")
_T = TypeVar("_T")


class ImplRecorder(Recorder, Generic[_P, _T]):
    trait_call: TraitCall
    path: type[Cell] | CellOf | None
    target: str | None = None

    @overload
    def __new__(
        cls, path: type[Cell] | CellOf | None, trait_call: TargetTraitCall[_P, _T]
    ) -> ImplRecorder[Concatenate[Selector, _P], _T]:
        ...

    @overload
    def __new__(cls, path: type[Cell] | CellOf | None, trait_call: TraitCall[_P, _T]) -> ImplRecorder[_P, _T]:
        ...

    def __new__(
        cls, path: type[Cell] | CellOf | None, trait_call: TraitCall[_P, _T]
    ) -> ImplRecorder[_P, _T] | ImplRecorder[Concatenate[Selector, _P], _T]:
        self = super().__new__(cls)
        self.path = path
        self.trait_call = trait_call
        return self

    def of(self, target: str):
        self.target = eval_dotpath(target, ctx_prefix.get())
        return self

    def signature(self):
        if isinstance(self.trait_call, TargetTraitCall):
            target = eval_dotpath(".", ctx_prefix.get())
        else:
            target = self.target
        return _Impl(target=target, path=self.path, trait_call=self.trait_call)  # type: ignore

    def __call__(self, content: Callable[Concatenate[Relationship, _P], Awaitable[_T]]):
        return super().__call__(content)


impl = ImplRecorder


class FetchRecorder(Recorder):
    resource: str

    def __init__(self, resource: str):
        self.resource = resource

    def signature(self):
        return _ResourceFatch(eval_dotpath(self.resource, ctx_prefix.get()) or ctx_prefix.get())

    def __call__(self, content: Callable[[Relationship, Selector], Awaitable[Any]]):
        return super().__call__(content)


fetch = FetchRecorder

_C = TypeVar("_C", bound="Cell")


class PullRecorder(Recorder, Generic[_C]):
    target: str | None = None
    path: type[Cell] | CellOf

    def __init__(self, path: type[_C] | CellOf[Unpack[tuple[Any, ...]], _C]):
        self.path = path

    def of(self, target: str):
        self.target = target
        return self

    def signature(self):
        return _Pull(eval_dotpath(self.target, ctx_prefix.get()) if self.target is not None else None, self.path)

    def __call__(self, content: Callable[[Relationship, Selector], Awaitable[_C]]):
        return super().__call__(content)


pull = PullRecorder


def completes(relative: str, output: str):
    r = get_current_namespace()
    r[CompleteRule(eval_dotpath(relative, ctx_prefix.get()))] = eval_dotpath(output, ctx_prefix.get())


def query(path: str):
    # TODO: Redesign, 主要是 Upper 的传递方式, 路径的自动组合之类的
    ...


class ImplDefaultTargetRecorder(Recorder):
    # trait_call: TraitCall
    path: type[Cell] | CellOf | None = None

    def __init__(self, path: type[Cell] | CellOf | None, trait_call: TraitCall):
        self.path = path
        self.trait_call = trait_call

    def signature(self):
        return ImplDefaultTarget(self.path, self.trait_call)

    def __call__(self, content: Callable[[Relationship], Selector]):
        return super().__call__(content)


default_target = ImplDefaultTargetRecorder
"""
def event_key(func: Callable[[Any], str]):
    r = get_current_namespace()
    r[EventKeyGetter()] = func
    return func

def event(key: str):
    def wrapper(func: Callable[[Any], Avilla])
"""
