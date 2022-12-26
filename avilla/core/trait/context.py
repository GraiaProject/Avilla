from __future__ import annotations

from collections.abc import Awaitable, Callable
from contextlib import contextmanager
from contextvars import ContextVar
from itertools import chain
from typing import (
    TYPE_CHECKING,
    Any,
    AsyncGenerator,
    Generic,
    MutableMapping,
    Protocol,
    TypeVar,
    overload,
)

from typing_extensions import Concatenate, ParamSpec, TypeAlias, Unpack

from ..metadata import Metadata, MetadataBound, MetadataOf, MetadataRoute
from ..resource import Resource
from ..selector import Selector
from . import (
    Fn,
    FnCall,
    Trait,
    UnappliedEntityFnCall,
    UnappliedMetadataFnCall,
    UnappliedUniversalFnCall,
)
from .signature import (
    ArtifactSignature,
    Bounds,
    ContextSourceSign,
    ElementParse,
    EventParse,
    Impl,
    Pull,
    Query,
    ResourceFetch,
    VisibleConf,
)

if TYPE_CHECKING:
    from ..account import AbstractAccount
    from ..context import Context
    from graia.amnesia.message import Element
    from ..event import AvillaEvent
    from ..protocol import BaseProtocol

Artifacts: TypeAlias = MutableMapping[ArtifactSignature, Any]

ctx_artifacts: ContextVar[Artifacts] = ContextVar("artifacts")


@contextmanager
def wrap_artifacts(*upstream_artifacts: Artifacts):
    artifacts = {}
    for upstream in upstream_artifacts:
        artifacts |= upstream
    token = ctx_artifacts.set(artifacts)
    yield artifacts
    ctx_artifacts.reset(token)


def get_artifacts() -> Artifacts:
    try:
        return ctx_artifacts.get()
    except LookupError:
        raise ValueError("cannot access artifacts due to undefined") from None


@contextmanager
def bounds(bound: str | MetadataBound, check: bool = True):
    parent = get_artifacts()
    override_artifacts = {}
    token = ctx_artifacts.set(override_artifacts)

    yield

    ctx_artifacts.reset(token)

    if check:
        referred_traits: dict[type[Trait], set[Fn]] = {}
        implemented_trait_fns: dict[type[Trait], set[Fn]] = {}

        for k in override_artifacts:
            if isinstance(k, Impl):
                implemented_trait_fns.setdefault(k.fn.trait, set()).add(k.fn)
                if k.fn.trait not in referred_traits:
                    referred_traits[k.fn.trait] = set(k.fn.trait.fn())

        if unimplemented := list(
            chain.from_iterable(
                fn_definations - implemented_trait_fns[trait] for trait, fn_definations in referred_traits.items()
            )
        ):
            raise NotImplementedError(f"missing required implements {unimplemented!r}")

    parent[Bounds(bound)] = override_artifacts


@contextmanager
def visible(checker: Callable[[Context], bool]):
    parent = get_artifacts()
    override_artifacts = {}
    token = ctx_artifacts.set(override_artifacts)

    yield

    parent[VisibleConf(checker)] = override_artifacts
    ctx_artifacts.reset(token)


_P = ParamSpec("_P")
_T = TypeVar("_T")
_T_co = TypeVar("_T_co", covariant=True)

RecordCallable = Callable[[_T], _T]


@overload
def implement(
    fn_call: UnappliedEntityFnCall[_P, _T_co]
) -> RecordCallable[Callable[Concatenate[Context, Selector, _P], Awaitable[_T_co]]]:
    ...


@overload
def implement(
    fn_call: UnappliedMetadataFnCall[_P, _T_co]
) -> RecordCallable[Callable[Concatenate[Context, MetadataOf, _P], Awaitable[_T_co]]]:
    ...


@overload
def implement(
    fn_call: UnappliedUniversalFnCall[_P, _T_co]
) -> RecordCallable[Callable[Concatenate[Context, Selector | MetadataOf, _P], Awaitable[_T_co]]]:
    ...


@overload
def implement(fn_call: FnCall[_P, _T_co]) -> RecordCallable[Callable[Concatenate[Context, _P], Awaitable[_T_co]]]:
    ...


def implement(fn_call: FnCall) -> ...:
    def wrapper(artifact):
        artifacts = get_artifacts()
        artifacts[Impl(fn_call.fn)] = artifact
        return artifact

    return wrapper


_MetadataT = TypeVar("_MetadataT", bound=Metadata)


def pull(
    route: type[_MetadataT] | MetadataRoute[Unpack[tuple[Any, ...]], _MetadataT]
) -> RecordCallable[Callable[[Context, Selector], Awaitable[_MetadataT]]]:
    def wrapper(artifact):
        artifacts = get_artifacts()
        artifacts[Pull(route)] = artifact
        return artifact

    return wrapper


_ResourceT = TypeVar("_ResourceT", bound=Resource)


def fetch(resource: type[_ResourceT]) -> RecordCallable[Callable[[Context, _ResourceT], Awaitable[Any]]]:
    def wrapper(artifact):
        artifacts = get_artifacts()
        artifacts[ResourceFetch(resource)] = artifact
        return artifact

    return wrapper


@overload
def query(pattern: str, /) -> RecordCallable[Callable[[Context, None, Selector], AsyncGenerator[Selector, None]]]:
    ...


@overload
def query(*pattern: str) -> RecordCallable[Callable[[Context, Selector, Selector], AsyncGenerator[Selector, None]]]:
    ...


def query(*pattern: ...) -> ...:
    def wrapper(artifact):
        artifacts = get_artifacts()
        artifacts[Query(".".join(pattern[:-1]) or None, pattern[-1])] = artifact
        return artifact

    return wrapper


def complete_rule():
    ...  # TODO


_ProtocolT = TypeVar("_ProtocolT", bound="BaseProtocol", contravariant=True)
_AccountT = TypeVar("_AccountT", bound="AbstractAccount", contravariant=True)


class _ContextSourceArtifact(Protocol[_AccountT]):
    async def __call__(self, account: _AccountT, target: Selector, *, via: Selector | None = None) -> Context:
        ...


class ContextSourceRecorder(Generic[_AccountT]):
    def __new__(cls, pattern: str):
        def wrapper(artifact: _ContextSourceArtifact[_AccountT]):
            artifacts = get_artifacts()
            artifacts[ContextSourceSign(pattern)] = artifact
            return artifact

        return wrapper

EventParser: TypeAlias = "Callable[[_ProtocolT, _AccountT, dict], Awaitable[tuple[AvillaEvent, Context]]]"

class EventParserRecorder(Generic[_ProtocolT, _AccountT]):
    def __new__(cls, event_type: str):
        def wrapper(handler: Callable[[_ProtocolT, _AccountT, dict], Awaitable[tuple[AvillaEvent, Context]]]):
            artifacts = get_artifacts()
            artifacts[EventParse(event_type)] = handler
            return handler

        return wrapper


ElementParser: TypeAlias = Callable[[Context, dict], Awaitable[Element]]


def element(element_type: str):
    def wrapper(handler: ElementParser):
        artifacts = get_artifacts()
        artifacts[ElementParse(element_type)] = handler
        return handler

    return wrapper
