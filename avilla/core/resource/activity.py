from typing import List, Optional, Tuple, Union
from avilla.core.service.entity import Activity, Status
from avilla.core.stream import Stream
from avilla.core.selectors import resource as resource_selector
from avilla.core.resource import ResourceMetaWrapper


class create(Activity[Status]):
    id: resource_selector


class write(Activity[Status]):
    data: bytes


class put(Activity[Tuple[Status, Union[resource_selector, None]]]):
    data: bytes


class read(Activity[Stream[bytes]]):
    pass


class stats(Activity[Status]):
    pass


class rename(Activity[Status]):
    to: resource_selector


class ls(Activity[List[resource_selector]]):
    parent: Optional[resource_selector] = resource_selector.dir["/"]


class remove(Activity[Status]):
    recursive: bool = False


class meta(Activity[ResourceMetaWrapper]):
    pass
