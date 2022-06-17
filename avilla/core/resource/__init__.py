from __future__ import annotations

from abc import ABCMeta, abstractmethod
from typing import TYPE_CHECKING, Generic, TypeVar

from avilla.core.metadata.model import Metadata

if TYPE_CHECKING:
    from avilla.core.relationship import Relationship
    from avilla.core.selectors import mainline


T = TypeVar("T")


class Resource(Generic[T]):
    mainline: mainline | None = None


R = TypeVar("R", bound=Resource)
M = TypeVar("M", bound=Metadata)


class ResourceProvider(metaclass=ABCMeta):
    @abstractmethod
    async def fetch(self, resource: Resource[T], relationship: Relationship | None = None) -> T:
        # TODO: 指导开发者使用 Relationship as a Guest, 以实现鉴权.
        pass
