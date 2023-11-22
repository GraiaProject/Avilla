from __future__ import annotations

from avilla.core.resource import Resource
from avilla.core.selector import Selector


class QQAPIResource(Resource[bytes]):
    content_type: str
    url: str
    filename: str | None = None
    height: str | None = None
    width: str | None = None
    size: str | None = None

    def __init__(
        self,
        selector: Selector,
        content_type: str,
        url: str,
        filename: str | None = None,
        height: str | None = None,
        width: str | None = None,
        size: str | None = None,
    ):
        super().__init__(selector)
        self.content_type = content_type
        self.url = url
        self.filename = filename
        self.height = height
        self.width = width
        self.size = size


class QQAPIImageResource(QQAPIResource):
    pass


class QQAPIAudioResource(QQAPIResource):
    pass


class QQAPIVideoResource(QQAPIResource):
    pass


class QQAPIFileResource(QQAPIResource):
    pass
