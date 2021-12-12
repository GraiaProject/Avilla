from typing import Generic, Optional, TypeVar

from avilla.core.stream import Stream

TMetadata = TypeVar("TMetadata")


class Resource(Generic[TMetadata]):
    stream: Stream
    metadata: Optional[TMetadata]

    def __init__(self, stream: Stream, metadata: Optional[TMetadata] = None):
        self.stream = stream
        self.metadata = metadata
