from __future__ import annotations

from abc import ABCMeta, abstractmethod
from typing import TYPE_CHECKING, Generic, TypeVar

from avilla.core.cell import Cell
from avilla.core.utilles.selector import Selector

if TYPE_CHECKING:
    from avilla.core.application import Avilla
    from avilla.core.protocol import BaseProtocol
    from avilla.core.relationship import Relationship


T = TypeVar("T")

# TODO: 解决 "Selector only" 模式下的类型标注问题.
class Resource(Generic[T]):
    id: str
    mainline: Selector | None = None

    @classmethod
    def get_default_provider(cls) -> ResourceProvider | None:
        ...

    @property
    @abstractmethod
    def resource_type(self) -> str:
        pass

    def to_selector(self) -> Selector:
        base_selector = self.mainline.copy() if self.mainline is not None else Selector()
        return base_selector.appendix(self.resource_type, self.id)


R = TypeVar("R", bound=Resource)
M = TypeVar("M", bound=Cell)


class ResourceProvider(metaclass=ABCMeta):
    @abstractmethod
    async def fetch(self, resource: Resource[T], relationship: Relationship | None = None) -> T:
        pass


_P = TypeVar("_P", bound="BaseProtocol")


class ProtocolResourceProvider(Generic[_P], ResourceProvider):
    protocol: _P

    def __init__(self, protocol: _P):
        self.protocol = protocol

    @abstractmethod
    async def fetch(self, resource: Resource[T], relationship: Relationship | None = None) -> T:
        pass

    @abstractmethod
    def get_resource_type(self) -> str:
        pass


def get_provider(
    resource: Resource,
    relationship: Relationship | None = None,
    protocol: BaseProtocol | None = None,
    avilla: Avilla | None = None,
) -> ResourceProvider | None:
    if relationship is not None:
        provider = (
            relationship.protocol.get_resource_provider(resource.to_selector())
            or relationship.avilla.get_resource_provider(resource.to_selector())
            or resource.get_default_provider()
        )
        if provider is not None:
            return provider
    if protocol is not None:
        provider = (
            protocol.get_resource_provider(resource.to_selector())
            or protocol.avilla.get_resource_provider(resource.to_selector())
            or resource.get_default_provider()
        )
        if provider is not None:
            return provider
    if avilla is not None:
        provider = avilla.get_resource_provider(resource.to_selector()) or resource.get_default_provider()
        if provider is not None:
            return provider
    return resource.get_default_provider()
