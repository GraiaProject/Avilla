from abc import ABCMeta, abstractmethod
from pathlib import Path
from typing import TYPE_CHECKING, Generic, Optional, Type, TypeVar, Union

from avilla.core.metadata.model import Metadata, MetadataModifies
from avilla.core.selectors import mainline

if TYPE_CHECKING:
    from avilla.core.relationship import Relationship


T = TypeVar("T")


class Resource(Generic[T]):
    mainline: Optional[mainline] = None


R = TypeVar("R", bound=Resource)
M = TypeVar("M", bound=Metadata)


class ResourceProvider(metaclass=ABCMeta):
    @abstractmethod
    async def fetch(self, resource: Resource[T], relationship: Optional["Relationship"] = None) -> T:
        # TODO: 指导开发者使用 Relationship as a Guest, 以实现鉴权.
        pass
