from __future__ import annotations

from abc import ABCMeta, abstractmethod
from typing import TYPE_CHECKING, Any, Awaitable, Callable, Dict, Generic, Type, TypeVar

if TYPE_CHECKING:
    from .model import Metadata, MetadataModifies


M = TypeVar("M", bound=Metadata)
T = TypeVar("T")


class MetadataSource(Generic[T, M], metaclass=ABCMeta):
    @abstractmethod
    async def fetch(self, target: T, model: Type[M]) -> M:
        ...

    @abstractmethod
    async def modify(self, target: T, modifies: MetadataModifies[T]) -> T:
        ...
