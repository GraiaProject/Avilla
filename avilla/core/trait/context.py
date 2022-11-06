from __future__ import annotations

from contextlib import contextmanager
from contextvars import ContextVar
from dataclasses import dataclass
from functools import reduce
from typing import Any, MutableMapping

from typing_extensions import TypeAlias

from . import Fn, Trait
from ..metadata import MetadataBound

from avilla.core.trait.signature import ArtifactSignature, Impl, Override, Bounds
from ..utilles.selector import Selector


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


@contextmanager
def overrides(
    client: str | None = None,
    endpoint: str | None = None,
    scene: str | None = None,
):
    parent = get_artifacts()
    override_artifacts = {}
    token = ctx_artifacts.set(override_artifacts)
    yield
    parent[Override(client, endpoint, scene)] = override_artifacts
    ctx_artifacts.reset(token)


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
