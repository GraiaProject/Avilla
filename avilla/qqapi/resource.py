from __future__ import annotations

from avilla.core.resource import Resource
from avilla.core.selector import Selector


class QQAPIResource(Resource[bytes]):
    url: str

    def __init__(self, selector: Selector, url: str):
        super().__init__(selector)
        self.url = url


class QQAPIImageResource(QQAPIResource):
    pass
