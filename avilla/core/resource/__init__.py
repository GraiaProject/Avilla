from abc import ABCMeta, abstractmethod
from contextlib import asynccontextmanager
from typing import AsyncGenerator, ClassVar, Dict, Set, Union

from avilla.core.operator import ResourceOperator
from avilla.core.selectors import resource as resource_selector


class ResourceProvider(metaclass=ABCMeta):
    supported_resource_types: ClassVar[Union[Set[str], Dict[str, int]]]

    @abstractmethod
    @asynccontextmanager
    def access_resource(self, res: resource_selector) -> AsyncGenerator["ResourceOperator", None]:
        ...
