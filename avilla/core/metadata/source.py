from __future__ import annotations

from abc import ABCMeta, abstractmethod
from typing import TYPE_CHECKING, Any, Callable, ClassVar, Coroutine, Generic, ParamSpec, Protocol, TypeVar
from typing_extensions import Self, Unpack

from avilla.core.metadata.model import Modify

if TYPE_CHECKING:
    from avilla.core.metadata.model import Metadata, MetadataModifies
    from avilla.core.utilles.selector import Selector


T = TypeVar("T", bound="Selector")
M = TypeVar("M", bound="Metadata")


"""
class MetadataSource(Generic[T, M], metaclass=ABCMeta):
    @abstractmethod
    async def fetch(self, target: T, model: type[M]) -> M:
        ...

    @abstractmethod
    async def modify(self, target: T, modifies: MetadataModifies[T]) -> T:
        ...
"""

class MetadataSource(Generic[T]):
    target: T

    _metadata_fetchers: ClassVar[dict[str, Callable[[Self, Unpack[tuple[str, ...]]], Coroutine[None, None, dict[str, Any]]]]] = {}
    _metadata_modifiers: ClassVar[dict[str, Callable[[Self, Unpack[tuple[Modify, ...]]], Coroutine[None, None, Any]]]] = {}
    _default_providers: ClassVar[dict[str, Callable[[Self], Any]]] = {}

    async def fetch(self, *fields: str) -> dict[str, Any]:
        if any(field not in self._metadata_fetchers for field in fields):
            raise NotImplementedError("Not implemented")
        result = {}
        for field in fields:
            if field in self._metadata_fetchers:
                result[field] = await self._metadata_fetchers[field](self, *fields)
            elif field in self._default_providers:
                result[field] = self._default_providers[field](self)
            else:
                raise NotImplementedError(f"Not implemented for field {field}")
        return result
    
    async def modify(self, modifies: list[Modify]):
        if any(modify.id not in self._metadata_modifiers for modify in modifies):
            raise NotImplementedError("Not implemented")
        for modify in modifies:
            if modify.id in self._metadata_modifiers:
                await self._metadata_modifiers[modify.id](self, modify)
            else:
                raise NotImplementedError(f"Not implemented for modify {modify.id}")
