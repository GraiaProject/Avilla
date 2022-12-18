from __future__ import annotations

from contextlib import contextmanager
from contextvars import ContextVar
from dataclasses import dataclass
from functools import reduce
from typing import (
    Any,
    Awaitable,
    Callable,
    MutableMapping,
    TypeVar,
    overload,
)

from typing_extensions import TypeAlias, Concatenate, ParamSpec

from ...context import Context
from ...utilles.selector import Selector
from ..metadata import MetadataBound
from . import BoundFn, Fn, Trait
from .signature import ArtifactSignature, Bounds, Impl


@dataclass(unsafe_hash=True)
class Scope:
    land: str
    mainline: str | None = None
    self: str | None = None


Artifacts: TypeAlias = "MutableMapping[ArtifactSignature, Any]"

ctx_artifacts: ContextVar[Artifacts] = ContextVar("artifacts")


@contextmanager
def wrap_artifacts(*upstraem_artifacts: Artifacts):
    artifacts = reduce(lambda a, b: {**a, **b}, upstraem_artifacts)
    token = ctx_artifacts.set(artifacts)
    yield artifacts
    ctx_artifacts.reset(token)


def get_artifacts() -> Artifacts:
    try:
        return ctx_artifacts.get()
    except LookupError:
        raise ValueError("cannot access artifacts due to undefined") from None


# TODO: 重新整理一遍 bounds 的形式


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


_P = ParamSpec("_P")
_T = TypeVar("_T")
_T_co = TypeVar("_T_co", covariant=True)

RecordCallable = Callable[[_T], _T]


@overload
def implement(fn: Fn[_P, _T_co]) -> RecordCallable[Callable[Concatenate[Context, _P], Awaitable[_T_co]]]:
    ...


@overload
def implement(
    fn: BoundFn[_P, _T_co]
) -> RecordCallable[Callable[Concatenate[Context, Selector | MetadataBound, _P], Awaitable[_T_co]]]:
    ...


def implement(fn: ...) -> ...:
    def wrapper(artifact):
        artifacts = get_artifacts()
        artifacts[Impl(fn)] = artifact
        return artifact

    return wrapper
