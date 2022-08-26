from __future__ import annotations

from contextlib import contextmanager
from contextvars import ContextVar
from dataclasses import dataclass
from typing import Any

from avilla.core.trait.signature import ArtifactSignature


@dataclass(unsafe_hash=True)
class Scope:
    land: str
    mainline: str | None = None
    self: str | None = None


Namespace = dict[Scope | None, dict[ArtifactSignature, Any]]

ctx_namespace: ContextVar[Namespace] = ContextVar("ctx_namespace")

GLOBAL_SCOPE = Scope(land="avilla")

ctx_scope: ContextVar[Scope] = ContextVar("ctx_scope", default=GLOBAL_SCOPE)
ctx_prefix: ContextVar[str] = ContextVar("ctx_prefix", default="")


@contextmanager
def scope(land: str, mainline: str | None = None, self: str | None = None):
    token = ctx_scope.set(Scope(land, mainline, self))
    yield
    ctx_scope.reset(token)


def eval_dotpath(path: str, env: str = "") -> str:
    if path.startswith("."):
        if env:
            return ".".join(i for i in env.split(".") + path.split(".") if i)
        raise ValueError("cannot parse relative path without env pattern")
    return path


@contextmanager
def prefix(pattern: str):
    token = ctx_prefix.set(eval_dotpath(pattern, ctx_prefix.get()))
    yield
    ctx_prefix.reset(token)


@contextmanager
def wrap_namespace(initial: Namespace | None = None):
    namespace: Namespace = initial or {}
    token = ctx_namespace.set(namespace)
    yield namespace
    ctx_namespace.reset(token)


def raise_for_no_namespace(exception: type[Exception] = LookupError):
    if ctx_namespace.get(None) is None:
        raise exception("required available namespace to initize")


def get_current_namespace() -> dict[ArtifactSignature, Any]:
    return ctx_namespace.get().setdefault(ctx_scope.get(), {})
