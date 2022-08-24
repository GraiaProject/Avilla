from __future__ import annotations

import abc
from typing import (
    TYPE_CHECKING,
    Any,
    AsyncGenerator,
    Awaitable,
    Callable,
    Concatenate,
    Generic,
    ParamSpec,
    Protocol,
    TypeVar,
    overload,
)

from typing_extensions import Unpack

from avilla.core.resource import Resource
from avilla.core.traitof import DirectFn, OrientedFn
from avilla.core.traitof.signature import CompleteRule
from avilla.core.traitof.signature import Impl as _Impl
from avilla.core.traitof.signature import ImplDefaultTarget
from avilla.core.traitof.signature import Pull as _Pull
from avilla.core.traitof.signature import Query
from avilla.core.traitof.signature import ResourceFetch as _ResourceFatch
from avilla.core.utilles.selector import Selector

from .context import ctx_prefix, eval_dotpath, get_current_namespace

if TYPE_CHECKING:
    from avilla.core.cell import Cell, CellOf
    from avilla.core.relationship import Relationship
    from avilla.core.traitof.signature import ArtifactSignature

    from . import Fn


class Recorder(abc.ABC):
    @abc.abstractmethod
    def signature(self) -> ArtifactSignature:
        ...

    def __call__(self, content: Any):
        sig = self.signature()
        r = get_current_namespace()
        r[sig] = content
        return content


_P = ParamSpec("_P")
_T = TypeVar("_T")


class ImplRecorder(Recorder, Generic[_P, _T]):
    trait_call: Fn
    path: type[Cell] | CellOf | None = None
    target: str | None = None

    @overload
    def __new__(cls, trait_call: OrientedFn[_P, _T]) -> ImplRecorder[Concatenate[Selector, _P], _T]:
        ...

    @overload
    def __new__(cls, trait_call: DirectFn[_P, _T]) -> ImplRecorder[Concatenate[Selector, _P], _T]:
        ...

    @overload
    def __new__(cls, trait_call: Fn[_P, _T]) -> ImplRecorder[_P, _T]:
        ...

    def __new__(cls, trait_call: Fn[_P, _T]) -> ImplRecorder[_P, _T] | ImplRecorder[Concatenate[Selector, _P], _T]:
        return super(ImplRecorder, cls).__new__(cls)

    def __init__(self, trait_call: Fn[_P, _T]):
        self.trait_call = trait_call

    def of(self, path: type[Cell] | CellOf):
        self.path = path
        return self

    def pin(self, target: str):
        self.target = eval_dotpath(target, ctx_prefix.get())
        return self

    def signature(self):
        if isinstance(self.trait_call, DirectFn):  # type: ignore
            target = eval_dotpath(".", ctx_prefix.get())
        else:
            target = self.target
        return _Impl(target=target, path=self.path, trait_call=self.trait_call)  # type: ignore

    def __call__(self, content: Callable[Concatenate[Relationship, _P], Awaitable[_T]]):
        return super().__call__(content)


impl = ImplRecorder

_R = TypeVar("_R", bound=Resource)


class FetchRecorder(Recorder, Generic[_R]):
    resource: type[_R]

    def __init__(self, resource: type[_R]):
        self.resource = resource

    def signature(self):
        return _ResourceFatch(self.resource)

    def __call__(self, content: Callable[[Relationship, _R], Awaitable[Any]]):
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

    def __call__(self, content: Callable[[Relationship, Selector | None], Awaitable[_C]]):
        return super().__call__(content)


pull = PullRecorder


def completes(relative: str, output: str):
    r = get_current_namespace()
    r[CompleteRule(eval_dotpath(relative, ctx_prefix.get()))] = eval_dotpath(output, ctx_prefix.get())



Querier = Callable[["Relationship", Selector | None, Selector], AsyncGenerator[Selector, None]]


@overload
def query(upper: None, target: str) -> Callable[[Callable[["Relationship", None, Selector], AsyncGenerator[Selector, None]]], Callable[["Relationship", None, Selector], AsyncGenerator[Selector, None]]]:
    ...

@overload
def query(upper: str, target: str) -> Callable[[Callable[["Relationship", Selector, Selector], AsyncGenerator[Selector, None]]], Callable[["Relationship", Selector, Selector], AsyncGenerator[Selector, None]]]:
    ...

def query(upper: str | None, target: str) -> ...:
    def wrapper(querier):
        r = get_current_namespace()
        r[Query(upper, target)] = querier
        return querier
    return wrapper


class ImplDefaultTargetRecorder(Recorder):
    # trait_call: TraitCall
    path: type[Cell] | CellOf | None = None

    def __init__(self, trait_call: Fn):
        self.trait_call = trait_call

    def of(self, path: type[Cell] | CellOf):
        self.path = path
        return self

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
