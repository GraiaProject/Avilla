from __future__ import annotations

from abc import ABCMeta, abstractmethod
from typing import TYPE_CHECKING, Generic, TypeVar

if TYPE_CHECKING:
    from avilla.core.metadata.model import Metadata, MetadataModifies
    from avilla.core.utilles.selector import Selector


T = TypeVar("T", bound="Selector")
M = TypeVar("M", bound="Metadata")


class MetadataSource(Generic[T, M], metaclass=ABCMeta):
    @abstractmethod
    async def fetch(self, target: T, model: type[M]) -> M:
        ...

    @abstractmethod
    async def modify(self, target: T, modifies: MetadataModifies[T]) -> T:
        ...
