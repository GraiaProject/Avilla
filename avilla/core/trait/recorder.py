from __future__ import annotations

import abc
from typing import (
    TYPE_CHECKING,
    Any,
    AsyncGenerator,
    Awaitable,
    Callable,
    Generic,
    TypeVar,
    overload,
)

from typing_extensions import Concatenate, ParamSpec, TypeAlias, Unpack

from avilla.core.resource import Resource
from avilla.core.trait import DirectFn, OrientedFn, Trait
from avilla.core.trait.signature import CastAllow, CompleteRule
from avilla.core.trait.signature import Impl as _Impl
from avilla.core.trait.signature import ImplDefaultTarget
from avilla.core.trait.signature import Pull as _Pull
from avilla.core.trait.signature import Query
from avilla.core.trait.signature import ResourceFetch as _ResourceFatch
from avilla.core.utilles.selector import Selector

from .context import ctx_prefix, eval_dotpath, get_current_namespace

if TYPE_CHECKING:
    from avilla.core.context import Context
    from avilla.core.metadata import Metadata, MetadataRoute
    from avilla.core.trait.signature import ArtifactSignature

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


class AlterRecorder(Recorder):
    @abc.abstractmethod
    def signature(self) -> ArtifactSignature:
        ...

    def __call__(self, content: Any):
        sig = self.signature()
        r = get_current_namespace()
        r.setdefault(sig, []).append(content)
        return content


_P = ParamSpec("_P")
_T = TypeVar("_T")


class ImplRecorder(Recorder, Generic[_P, _T]):
    trait_call: Fn
    path: type[Metadata] | MetadataRoute | None = None
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

    def of(self, path: type[Metadata] | MetadataRoute):
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

    def __call__(self, content: Callable[Concatenate[Context, _P], Awaitable[_T]]):
        return super().__call__(content)


impl = ImplRecorder

_R = TypeVar("_R", bound=Resource)


class FetchRecorder(Recorder, Generic[_R]):
    resource: type[_R]

    def __init__(self, resource: type[_R]):
        self.resource = resource

    def signature(self):
        return _ResourceFatch(self.resource)

    def __call__(self, content: Callable[[Context, _R], Awaitable[Any]]):
        return super().__call__(content)


fetch = FetchRecorder

_M = TypeVar("_M", bound="Metadata")


class PullRecorder(Recorder, Generic[_M]):
    target: str | None = None
    path: type[Metadata] | MetadataRoute

    def __init__(self, path: type[_M] | MetadataRoute[Unpack[tuple[Any, ...]], _M]):
        self.path = path

    def of(self, target: str):
        self.target = target
        return self

    def signature(self):
        return _Pull(eval_dotpath(self.target, ctx_prefix.get()) if self.target is not None else None, self.path)

    def __call__(self, content: Callable[[Context, Selector | None], Awaitable[_M]]):
        return super().__call__(content)


pull = PullRecorder


def completes(relative: str, output: str):
    r = get_current_namespace()
    r[CompleteRule(eval_dotpath(relative, ctx_prefix.get()))] = eval_dotpath(output, ctx_prefix.get())


Querier: TypeAlias = "Callable[[Context, Selector | None, Selector], AsyncGenerator[Selector, None]]"


@overload
def query(
    upper: None, target: str
) -> Callable[
    [Callable[["Context", None, Selector], AsyncGenerator[Selector, None]]],
    Callable[["Context", None, Selector], AsyncGenerator[Selector, None]],
]:
    ...


@overload
def query(
    upper: str, target: str
) -> Callable[
    [Callable[["Context", Selector, Selector], AsyncGenerator[Selector, None]]],
    Callable[["Context", Selector, Selector], AsyncGenerator[Selector, None]],
]:
    ...


def query(upper: str | None, target: str) -> ...:
    def wrapper(querier):
        r = get_current_namespace()
        r[Query(upper, target)] = querier
        return querier

    return wrapper


def casts(trait_type: type[Trait], target: str | None = None):
    r: dict[ArtifactSignature, Any] = get_current_namespace()
    r[CastAllow(trait_type, target)] = True


class ImplDefaultTargetRecorder(Recorder):
    # trait_call: TraitCall
    path: type[Metadata] | MetadataRoute | None = None

    def __init__(self, trait_call: Fn):
        self.trait_call = trait_call

    def of(self, path: type[Metadata] | MetadataRoute):
        self.path = path
        return self

    def signature(self):
        return ImplDefaultTarget(self.path, self.trait_call)

    def __call__(self, content: Callable[[Context], Selector]):
        return super().__call__(content)


default_target = ImplDefaultTargetRecorder
