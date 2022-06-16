from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING

from avilla.core.resource import Resource, ResourceProvider

if TYPE_CHECKING:
    from avilla.core.relationship import Relationship


class LocalFileResource(Resource[bytes]):
    file: Path

    def __init__(self, file: Path | str):
        if isinstance(file, str):
            file = Path(file)
        self.file = file


class LocalFileResourceProvider(ResourceProvider):
    async def fetch(self, resource: LocalFileResource, relationship: Relationship | None = None):
        if isinstance(resource, LocalFileResource):
            return resource.file.read_bytes()
