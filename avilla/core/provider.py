import abc
from dataclasses import dataclass
from pathlib import Path
from typing import Generic, TypeVar, Union

import aiofiles

T = TypeVar("T")


@dataclass
class Provider(abc.ABC, Generic[T]):
    __annotations__ = {}

    @abc.abstractmethod
    async def __call__(self) -> T:
        raise NotImplementedError()


class FileProvider(Provider[bytes]):
    path: Path

    def __init__(self, path: Union[Path, str]):
        if isinstance(path, str):
            path = Path(path)
        self.path = path

    async def __call__(self) -> bytes:
        async with aiofiles.open(str(self.path), "rb") as f:
            return await f.read()


class RawProvider(Provider[bytes]):
    raw: bytes

    def __init__(self, raw: bytes):
        self.raw = raw

    async def __call__(self) -> bytes:
        return self.raw


class HttpGetProvider(Provider[bytes]):
    url: str

    def __init__(self, url: str):
        self.url = url

    async def __call__(self) -> bytes:
        import aiohttp

        async with aiohttp.ClientSession() as session:
            async with session.get(self.url) as resp:
                return await resp.read()
