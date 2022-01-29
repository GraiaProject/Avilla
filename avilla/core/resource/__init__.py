from abc import ABCMeta, abstractmethod
from contextlib import asynccontextmanager
from typing import AsyncGenerator, ClassVar, Set

from avilla.core.selectors import resource as resource_selector
from avilla.core.operator import ResourceOperator

class ResourceProvider(metaclass=ABCMeta):
    supported_resource_types: ClassVar[Set[str]]

    @abstractmethod
    @asynccontextmanager
    def access_resource(self, res: resource_selector) -> AsyncGenerator["ResourceOperator", None]:
        ...
