from __future__ import annotations

from pathlib import Path
from typing import Generic, TypeVar

from avilla.core.selector import Selector

from .metadata import Metadata

T = TypeVar("T")


class Resource(Metadata, Generic[T]):
    selector: Selector

    def __init__(self, selector: Selector):
        self.selector = selector

    def to_selector(self):
        return self.selector


class LocalFileResource(Resource[bytes]):
    file: Path

    def __init__(self, file: Path | str):
        if isinstance(file, str):
            file = Path(file)
        self.file = file

    @property
    def selector(self) -> Selector:
        return Selector().land("avilla-core").local_file(str(self.file))


class RawResource(Resource[T]):
    data: T

    def __init__(self, data: T):
        self.data = data

    @property
    def selector(self):
        return Selector().land("avilla-core").raw_data(str(id(self)))


class UrlResource(Resource[bytes]):
    def __init__(self, url: str):
        self.url = url

    @property
    def selector(self):
        return Selector().land("avilla-core").url(self.url)
