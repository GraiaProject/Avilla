from __future__ import annotations

from pathlib import Path
from typing import Generic, TypeAlias, TypeVar

from avilla.core.cell import Cell
from avilla.core.utilles.selector import Selector

T = TypeVar("T")


class Resource(Cell, Generic[T]):
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
