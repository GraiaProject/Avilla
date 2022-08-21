from __future__ import annotations

from contextlib import contextmanager
from contextvars import ContextVar
from dataclasses import dataclass
from typing import TYPE_CHECKING, Any

from avilla.core.traitof.signature import ArtifactSignature

if TYPE_CHECKING:
    from avilla.core.cell import Cell, CellOf


@dataclass(unsafe_hash=True)
class Scope:
    mainline: str | None = None
    self: str | None = None


Namespace = dict[Scope | None, dict[ArtifactSignature, Any]]

ctx_namespace: ContextVar[Namespace] = ContextVar("ctx_namespace")

GLOBAL_SCOPE = Scope()

ctx_scope: ContextVar[Scope] = ContextVar("ctx_scope", default=GLOBAL_SCOPE)
ctx_prefix: ContextVar[str] = ContextVar("ctx_prefix", default="")


@contextmanager
def scope(mainline: str | None = None, self: str | None = None, auto_prefix: bool = True):
    token = ctx_scope.set(Scope(mainline, self))
    token_prefix = ctx_prefix.set(mainline) if auto_prefix and mainline else None
    yield
    if token_prefix is not None:
        ctx_prefix.reset(token_prefix)
    ctx_scope.reset(token)


def eval_dotpath(path: str, env: str = "") -> str:
    if path.startswith("."):
        if env:
            return env + path
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
