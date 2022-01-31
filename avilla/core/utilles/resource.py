from contextlib import asynccontextmanager
from pathlib import Path
from typing import Any, AsyncGenerator

from avilla.core.operator import OperatorCache, ResourceOperator
from avilla.core.resource import ResourceProvider
from avilla.core.selectors import resource as resource_selector
from avilla.core.service.entity import Status
from avilla.core.stream import Stream
from avilla.core.utilles import as_asynciter


class LocalFileOperator(ResourceOperator):
    path: Path

    def __init__(self, path: Path) -> None:
        self.path = path

    async def operate(self, operator: str, target: Any, value: Any, cache: OperatorCache = None) -> Any:
        if operator == "create":
            if self.path.exists():
                raise ValueError(f"{self.path} already exists.")
            self.path.parent.mkdir(parents=True, exist_ok=True)
            self.path.touch()
        elif operator == "write":
            self.path.write_bytes(value)
        elif operator == "put":
            self.path.touch()
            self.path.write_bytes(value)
            return (
                Status(True, "ok"),
                resource_selector.file[str(self.path)].provider[LocalFileResourceProvider],
            )
        elif operator == "read":
            return Status(True, "ok"), Stream(self.path.read_bytes())
        elif operator == "stats":
            if self.path.exists():
                return Status(True, "ok")
            return Status(False, "not found")
        elif operator == "ls":
            return as_asynciter(self.path.iterdir())
        elif operator == "cover":
            self.path.rename(list(value.path.values())[0])
            return Status(True, "ok")
        elif operator == "remove":
            self.path.unlink()
            return Status(True, "ok")
        elif operator == "meta":
            raise NotImplementedError
        else:
            raise ValueError(f"{operator} is not a valid operator.")


class LocalFileResourceProvider(ResourceProvider):
    supported_resource_types = {"file": 16}

    @asynccontextmanager
    async def access_resource(self, res: resource_selector) -> AsyncGenerator["ResourceOperator", None]:
        yield LocalFileOperator(Path(list(res.path.values())[0]))
