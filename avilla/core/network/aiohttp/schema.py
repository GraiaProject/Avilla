from typing import Dict, Literal

from yarl import URL

from avilla.core.network.schema import Schema


class ClientSchema(Schema):
    pattern = "$client"


class HttpRequestSchema(Schema):
    pattern = "$client"
    url: URL
    method: Literal["GET", "POST", "PUT", "DELETE"]
    data: bytes
    headers: Dict[str, str]

    def __init__(
        self,
        url: URL,
        method: Literal["GET", "POST", "PUT", "DELETE"],
        data: bytes,
        headers: Dict[str, str] = None,
    ):
        self.url = url
        self.method = method
        self.data = data
        self.headers = headers or {}
