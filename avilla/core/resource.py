from __future__ import annotations

from pathlib import Path
from typing import Generic, TypeVar

from typing_extensions import TypeAlias

from avilla.core.selector import Selector

from .metadata import Metadata

T = TypeVar("T")


class Resource(Metadata, Generic[T]):
    selector: Selector

    def __init__(self, selector: Selector):
        self.selector = selector

    def to_selector(self):
        return self.selector


BlobResource: TypeAlias = Resource[bytes]


class LocalFileResource(BlobResource):
    file: Path

    def __init__(self, file: Path | str):
        if isinstance(file, str):
            file = Path(file)
        self.file = file

    @property
    def selector(self) -> Selector:
        return Selector().land("avilla-core").local_file(str(self.file))
