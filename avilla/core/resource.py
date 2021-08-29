from typing import Generic, Optional, TypeVar

from avilla.core.provider import Provider

TMetadata = TypeVar("TMetadata")


class Resource(Generic[TMetadata]):
    provider: Provider
    metadata: Optional[TMetadata]

    def __init__(self, provider: Provider, metadata: Optional[TMetadata] = None):
        self.provider = provider
        self.metadata = metadata
