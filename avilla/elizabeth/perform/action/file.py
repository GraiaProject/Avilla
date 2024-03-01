from __future__ import annotations

import io
import os
from datetime import timedelta
from typing import TYPE_CHECKING

from graia.amnesia.builtins.memcache import Memcache, MemcacheService

from avilla.core.ryanvk.collector.account import AccountCollector
from avilla.core.selector import Selector
from avilla.elizabeth.file import (
    FileData,
    FileUpload,
    FileDirectoryCreate,
    FileDelete,
    FileMove,
    FileRename,
)

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
        file = FileData.parse(result)
        await cache.set(
            f"elizabeth/account({self.account.route['account']}).group({target['group']}).file({target['file']})", file,
            timedelta(minutes=5),
        )
        return file

    @m.entity(FileUpload.upload, target="land.group")
    async def upload_file(
        self,
        target: Selector,
        name: str,
        file: bytes | io.IOBase | os.PathLike,
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

    @m.entity(FileDirectoryCreate.create, target="land.group")
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

    @m.entity(FileDelete.delete, target="land.group.file")
    async def delete_file(self, target: Selector) -> None:
         await self.account.connection.call(
            "update",
            "file_delete",
            {
                "id": target["file"],
                "target": int(target["group"]),
            },
        )

    @m.entity(FileMove.move, target="land.group.file")
    async def move_file(self, target: Selector, to: Selector) -> None:
         await self.account.connection.call(
            "update",
            "file_move",
            {
                "id": target["file"],
                "target": int(target["group"]),
                "moveTo": to["file"],
            },
        )

    @m.entity(FileRename.rename, target="land.group.file")
    async def rename_file(self, target: Selector, name: str) -> None:
         await self.account.connection.call(
            "update",
            "file_rename",
            {
                "id": target["file"],
                "target": int(target["group"]),
                "renameTo": name,
            },
        )
