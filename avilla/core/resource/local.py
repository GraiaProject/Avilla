
from pathlib import Path
from typing import Optional, Union
from avilla.core.metadata import Metadata
from avilla.core.resource import Resource, ResourceProvider


class LocalFileResource(Resource[bytes]):
    file: Path

    def __init__(self, file: Union[Path, str]):
        if isinstance(file, str):
            file = Path(file)
        self.file = file

class LocalFile(Metadata):
    file: Path
    name: str


class LocalFileResourceProvider(ResourceProvider):
    async def fetch(self, resource: LocalFileResource, relationship: Optional["Relationship"] = None):
        if isinstance(resource, LocalFileResource):
            return resource.file.read_bytes()
    
    async def meta(self, resource: LocalFileResource, meta_class):
        if isinstance(resource, LocalFileResource)