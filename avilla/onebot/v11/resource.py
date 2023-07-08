from __future__ import annotations

from avilla.core.resource import Resource
from avilla.core.selector import Selector


class OneBot11Resource(Resource[bytes]):
    file: str
    url: str

    def __init__(self, selector: Selector, file: str, url: str):
        super().__init__(selector)
        self.file = file
        self.url = url


class OneBot11ImageResource(OneBot11Resource):
    pass


class OneBot11RecordResource(OneBot11Resource):
    pass


class OneBot11VideoResource(OneBot11Resource):
    pass


class OneBot11FileResource(OneBot11Resource):
    name: str
    size: int
    busid: int

    def __init__(self, selector: Selector, file: str, url: str, name: str, size: int, busid: int):
        super().__init__(selector, file, url)
        self.name = name
        self.size = size
        self.busid = busid
