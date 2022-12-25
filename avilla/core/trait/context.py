from __future__ import annotations

from contextlib import contextmanager
from contextvars import ContextVar
from functools import reduce
from typing import Any, Awaitable, Callable, MutableMapping, TypeVar, overload

from typing_extensions import Concatenate, ParamSpec, TypeAlias, Unpack

from ..context import Context
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
from .signature import ArtifactSignature, Bounds, Impl, Pull, ResourceFetch, VisibleConf

Artifacts: TypeAlias = "MutableMapping[ArtifactSignature, Any]"

ctx_artifacts: ContextVar[Artifacts] = ContextVar("artifacts")


@contextmanager
def wrap_artifacts(*upstream_artifacts: Artifacts):
    artifacts = reduce(lambda a, b: {**a, **b}, upstream_artifacts)
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

    if check:
        referred_traits: dict[type[Trait], set[Fn]] = {}
        implemented_trait_fns: dict[type[Trait], set[Fn]] = {}

        for k in override_artifacts:
            if isinstance(k, Impl):
                if k.fn.trait not in referred_traits:
                    referred_fn = set()
                    referred_traits[k.fn.trait] = referred_fn
                else:
                    referred_fn = referred_traits[k.fn.trait]
                referred_fn.update(k.fn.trait.fn())

                implemented_fn = implemented_trait_fns.setdefault(k.fn.trait, set())
                implemented_fn.add(k.fn)

        for trait, fn_definations in referred_traits.items():
            if not implemented_trait_fns[trait].issuperset(fn_definations):
                unimplemented = list(fn_definations - implemented_trait_fns[trait])
                raise NotImplementedError(f"missing required implements {unimplemented!r}")

    parent[Bounds(bound)] = override_artifacts
    ctx_artifacts.reset(token)


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


def complete_rule():
    ...  # TODO
