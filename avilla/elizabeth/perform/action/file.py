from __future__ import annotations

import os
from datetime import timedelta
from typing import IO, TYPE_CHECKING

from graia.amnesia.builtins.memcache import Memcache, MemcacheService

from avilla.core.ryanvk.collector.account import AccountCollector
from avilla.core.selector import Selector
from avilla.standard.core.file import (
    FileData,
    FileCapability,
    FileDirectoryCapability
)

from avilla.elizabeth.utils import filedata_parse

if TYPE_CHECKING:
    from avilla.elizabeth.account import ElizabethAccount  # noqa
    from avilla.elizabeth.protocol import ElizabethProtocol  # noqa


class ElizabethAnnouncementActionPerform((m := AccountCollector["ElizabethProtocol", "ElizabethAccount"]())._):
    m.namespace = "avilla.protocol/elizabeth::action"
    m.identify = "file"

    @m.pull("land.group.file", FileData)
    async def get_file(self, target: Selector, route: ...) -> FileData:
        cache: Memcache = self.protocol.avilla.launch_manager.get_component(MemcacheService).cache
        if file := await cache.get(
            f"elizabeth/account({self.account.route['account']}).group({target['group']}).file({target['file']})"
        ):
            return file
        result = await self.account.connection.call(
            "fetch",
            "file_info",
            {
                "id": target["file"],
                "target": int(target["group"]),
                "withDownloadInfo": "True",
            },
        )
        file = filedata_parse(result)
        await cache.set(
            f"elizabeth/account({self.account.route['account']}).group({target['group']}).file({target['file']})", file,
            timedelta(minutes=5),
        )
        return file

    @m.entity(FileCapability.upload, target="land.group")
    async def upload_file(
        self,
        target: Selector,
        name: str,
        file: bytes | IO[bytes] | os.PathLike,
        path: str | None = None,
    ) -> Selector:
        _name = name or ""
        _path = path or ""
        if "/" in _path and not _name:
            _path, _name = _path.rsplit("/", 1)

        if isinstance(file, os.PathLike):
            file = open(file, "rb")

        result = await self.account.connection.call(
            "multipart",
            "file_upload",
            {
                "type": "group",
                "target": str(target["group"]),
                "path": _path,
                "file": {"value": file, **({"filename": _name} if _name else {})},
            },
        )
        return target.file(str(result["id"]))

    @m.entity(FileDirectoryCapability.create, target="land.group")
    async def create_directory(self, target: Selector, name: str, parent: str | None = None) -> Selector:
        result = await self.account.connection.call(
            "update",
            "file_mkdir",
            {
                "id": parent or "",
                "directoryName": name,
                "target": int(target["group"]),
            },
        )
        return target.file(result["id"])

    @m.entity(FileCapability.delete, file="land.group.file")
    async def delete_file(self, file: Selector, busid: int | None = None) -> None:
        await self.account.connection.call(
            "update",
            "file_delete",
            {
                "id": file["file"],
                "target": int(file["group"]),
            },
        )

    @m.entity(FileDirectoryCapability.delete, file="land.group.file")
    async def delete_folder(self, file: Selector) -> None:
        await self.account.connection.call(
            "update",
            "file_delete",
            {
                "id": file["file"],
                "target": int(file["group"]),
            },
        )

    @m.entity(FileCapability.move, file="land.group.file")
    @m.entity(FileDirectoryCapability.move, file="land.group.file")
    async def move_file(self, file: Selector, to: Selector) -> None:
        await self.account.connection.call(
            "update",
            "file_move",
            {
                "id": file["file"],
                "target": int(file["group"]),
                "moveTo": to["file"],
            },
        )

    @m.entity(FileCapability.rename, file="land.group.file")
    @m.entity(FileDirectoryCapability.rename, file="land.group.file")
    async def rename_file(self, file: Selector, name: str) -> None:
        await self.account.connection.call(
            "update",
            "file_rename",
            {
                "id": file["file"],
                "target": int(file["group"]),
                "renameTo": name,
            },
        )
