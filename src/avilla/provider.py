from dataclasses import dataclass
import abc
from typing import Generic, TypeVar
import aiofiles
from pathlib import Path

T = TypeVar("T")


@dataclass
class Provider(abc.ABC, Generic[T]):
    @abc.abstractmethod
    async def fetch(self) -> T:
        raise NotImplementedError()


class FileProvider(Provider[bytes]):
    path: Path

    def __init__(self, path: Path):
        self.path = path

    async def fetch(self) -> bytes:
        async with aiofiles.open(str(self.path), "rb") as f:
            return await f.read()


class RawProvider(Provider[bytes]):
    raw: bytes

    def __init__(self, raw: bytes):
        self.raw = raw

    async def fetch(self) -> bytes:
        return self.raw
