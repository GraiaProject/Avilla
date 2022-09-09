from __future__ import annotations
from contextvars import ContextVar
from typing import TYPE_CHECKING, Any, Awaitable, Callable, TypeVar

from avilla.core.trait import Fn, Trait
from avilla.core.trait.signature import ExtensionImpl

if TYPE_CHECKING:
    from avilla.core.relationship import Relationship


class FnExtension:
    def set_group(self, group: str):
        ...


ctx_fnextensions: ContextVar[dict[str, list[FnExtension]]] = ContextVar("fnextensions")


E = TypeVar("E", bound=FnExtension)

class ExtensionHandler:
    rs: Relationship
    trait: Trait
    fn: Fn

    _artifacts: dict[ExtensionImpl, list[Callable[[Relationship, FnExtension], Awaitable[Any]]]]

    def __init__(self, rs: Relationship, trait: Trait, fn: Fn):
        self.rs = rs
        self.trait = trait
        self.fn = fn

        self._artifacts = {k: v for k, v in rs._artifacts.items() if isinstance(k, ExtensionImpl)}
    
    def add_impl(self, signature: ExtensionImpl, impl: Callable[[Relationship, FnExtension], Awaitable[Any]]):
        self._artifacts.setdefault(signature, []).append(impl)
    
    def impl(self, signature: ExtensionImpl[E]):
        def wrapper(impl: Callable[[Relationship, E], Awaitable[Any]]):
            self._artifacts.setdefault(signature, []).append(impl)  # type: ignore
            return impl
        return wrapper

    def handle_extensions(self):
        ext = ctx_fnextensions.get()
        for group, exts in ext.items():
            exts