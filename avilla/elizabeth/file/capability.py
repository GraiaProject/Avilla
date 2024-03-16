from __future__ import annotations

import os
from typing import IO

from avilla.core.ryanvk import Fn, TargetOverload
from avilla.core.selector import Selector
from graia.ryanvk.capability import Capability


class FileUpload(Capability):
    @Fn.complex({TargetOverload(): ["target"]})
    async def upload(
        self, target: Selector, name: str, file: bytes | IO[bytes] | os.PathLike, path: str | None = None
    ) -> Selector:
        ...


class FileDirectoryCreate(Capability):
    @Fn.complex({TargetOverload(): ["target"]})
    async def create(
        self, target: Selector, name: str, parent: str | None = None
    ) -> Selector:
        ...


class FileDelete(Capability):
    @Fn.complex({TargetOverload(): ["file"]})
    async def delete(
        self, file: Selector,
    ) -> None:
        ...


class FileMove(Capability):
    @Fn.complex({TargetOverload(): ["file"]})
    async def move(
        self, file: Selector, to: Selector
    ) -> None:
        ...


class FileRename(Capability):
    @Fn.complex({TargetOverload(): ["file"]})
    async def rename(
        self, file: Selector, name: str
    ) -> None:
        ...