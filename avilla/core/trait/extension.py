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

    _artifacts: dict[ExtensionImpl, Callable[[Relationship, FnExtension], Awaitable[Any]]]

    def __init__(self, rs: Relationship):
        self.rs = rs

        self._artifacts = {k: v for k, v in rs._artifacts.items() if isinstance(k, ExtensionImpl)}
    
    def add_impl(self, signature: ExtensionImpl, impl: Callable[[Relationship, FnExtension], Awaitable[Any]]):
        self._artifacts[signature] = impl
    
    def impl(self, signature: ExtensionImpl[E]):
        def wrapper(impl: Callable[[Relationship, E], Awaitable[Any]]):
            self._artifacts[signature] = impl  # type: ignore
            return impl
        return wrapper

    async def handle_extensions(self):
        ext = ctx_fnextensions.get()
        impl_map = {}
        failed_group = []
        for group, exts in ext.items():
            failed_all: bool = True

            for ext in exts:
                ext.set_group(group)
                if (impl := self._artifacts.get(ExtensionImpl(type(ext)))) is not None:
                    failed_all = False
                    # await impl(self.rs, ext)
                    impl_map.setdefault(impl, []).append(ext)

            if failed_all:
                failed_group.append(group)

        if failed_group:
            raise NotImplementedError(
                f"groups {repr(failed_group)} cannot be displayed due to all attempt for apply failed"
            )
        
        for impl, impl_ext in impl_map.items():
            for ext in impl_ext:
                await impl(self.rs, ext)
