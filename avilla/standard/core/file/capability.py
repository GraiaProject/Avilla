from __future__ import annotations

import os
from typing import IO

from avilla.core.ryanvk import Fn, TargetOverload
from avilla.core.selector import Selector
from graia.ryanvk.capability import Capability


class FileDirectoryCapability(Capability):
    @Fn.complex({TargetOverload(): ["target"]})
    async def create(
        self, target: Selector, name: str, parent: str | None = None
    ) -> Selector | None:
        ...

    @Fn.complex({TargetOverload(): ["file"]})
    async def delete(
        self, file: Selector,
    ) -> None:
        ...

    @Fn.complex({TargetOverload(): ["file"]})
    async def move(
        self, file: Selector, to: Selector
    ) -> None:
        ...

    @Fn.complex({TargetOverload(): ["file"]})
    async def rename(
        self, file: Selector, name: str
    ) -> None:
        ...

class FileCapability(Capability):
    @Fn.complex({TargetOverload(): ["target"]})
    async def upload(
        self, target: Selector, name: str, file: bytes | IO[bytes] | os.PathLike, path: str | None = None
    ) -> Selector | None:
        ...

    @Fn.complex({TargetOverload(): ["file"]})
    async def delete(
        self, file: Selector, busid: int | None = None
    ) -> None:
        ...

    @Fn.complex({TargetOverload(): ["file"]})
    async def move(
        self, file: Selector, to: Selector
    ) -> None:
        ...

    @Fn.complex({TargetOverload(): ["file"]})
    async def rename(
        self, file: Selector, name: str
    ) -> None:
        ...