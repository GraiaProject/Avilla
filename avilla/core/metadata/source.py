from __future__ import annotations

from abc import ABCMeta, abstractmethod
from typing import TYPE_CHECKING, Generic, TypeVar

if TYPE_CHECKING:
    from avilla.core.metadata.model import Metadata, MetadataModifies


M = TypeVar("M", bound="Metadata")
T = TypeVar("T")


class MetadataSource(Generic[T, M], metaclass=ABCMeta):
    @abstractmethod
    async def fetch(self, target: T, model: type[M]) -> M:
        ...

    @abstractmethod
    async def modify(self, target: T, modifies: MetadataModifies[T]) -> T:
        ...
