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

from ..resource import Resource
from .signature import Impl as _Impl
from .signature import Pull as _Pull
from .signature import Query
from .signature import ResourceFetch as _ResourceFatch
from avilla.core.utilles.selector import Selector

from .context import get_artifacts

if TYPE_CHECKING:
    from avilla.core.context import Context
    from ..metadata import Metadata, MetadataRoute
    from .signature import ArtifactSignature

    from . import Fn


class Recorder(abc.ABC):
    @abc.abstractmethod
    def signature(self) -> ArtifactSignature:
        ...

    def __call__(self, content: Any):
        sig = self.signature()
        r = get_artifacts()
        r[sig] = content
        return content


class AlterRecorder(Recorder):
    @abc.abstractmethod
    def signature(self) -> ArtifactSignature:
        ...

    def __call__(self, content: Any):
        sig = self.signature()
        r = get_artifacts()
        r.setdefault(sig, []).append(content)
        return content


_P = ParamSpec("_P")
_T = TypeVar("_T")


class ImplRecorder(Recorder, Generic[_P, _T]):
    fn: Fn

    def __new__(cls, fn: Fn[_P, _T]) -> ImplRecorder[_P, _T]:
        return super(ImplRecorder, cls).__new__(cls)

    def __init__(self, fn: Fn[_P, _T]):
        self.fn = fn

    def signature(self):
        return _Impl(self.fn)

    def __call__(self, content: Callable[Concatenate[Context, Selector, _P], Awaitable[_T]]):
        return super().__call__(content)


_R = TypeVar("_R", bound=Resource)


class FetchRecorder(Recorder, Generic[_R]):
    resource: type[_R]

    def __init__(self, resource: type[_R]):
        self.resource = resource

    def signature(self):
        return _ResourceFatch(self.resource)

    def __call__(self, content: Callable[[Context, _R], Awaitable[Any]]):
        return super().__call__(content)


_M = TypeVar("_M", bound="Metadata")


class PullRecorder(Recorder, Generic[_M]):
    route: type[Metadata] | MetadataRoute

    def __init__(self, route: type[_M] | MetadataRoute[Unpack[tuple[Any, ...]], _M]):
        self.route = route

    def of(self, target: str):
        self.target = target
        return self

    def signature(self):
        return _Pull(self.route)

    def __call__(self, content: Callable[[Context, Selector | None], Awaitable[_M]]):
        return super().__call__(content)

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
        r = get_artifacts()
        r[Query(upper, target)] = querier
        return querier

    return wrapper


impl = ImplRecorder
fetch = FetchRecorder
pull = PullRecorder
