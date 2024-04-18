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
from avilla.onebot.v11.utils import file_parse, folder_parse
from pathlib import Path
from tempfile import NamedTemporaryFile

if TYPE_CHECKING:
    from avilla.onebot.v11.account import OneBot11Account  # noqa
    from avilla.onebot.v11.protocol import OneBot11Protocol  # noqa


class OneBot11AnnouncementActionPerform((m := AccountCollector["OneBot11Protocol", "OneBot11Account"]())._):
    m.namespace = "avilla.protocol/onebot11::action"
    m.identify = "file"

    @m.pull("land.group.file", FileData)
    async def get_file(self, target: Selector, route: ...) -> FileData:
        cache: Memcache = self.protocol.avilla.launch_manager.get_component(MemcacheService).cache
        if file := await cache.get(
            f"onebot11/account({self.account.route['account']}).group({target['group']}).file({target['file']})"
        ):
            return file

        async def step(data: FileData):
            res2 = await self.account.connection.call(
                "get_group_files_by_folder",
                {
                    "group_id": int(target["group"]),
                    "folder_id": data.id,
                },
            )
            if not res2:
                raise RuntimeError(f"File {target} not found.")
            for file in res2["files"]:
                _res = await self.account.connection.call(
                    "get_group_file_url",
                    {
                        "group_id": int(target["group"]),
                        "file_id": file["file_id"],
                        "busid": file["busid"],
                    },
                )
                filedata = file_parse(file, _res["url"] if _res else "", data)
                if filedata.id == target["file"]:
                    await cache.set(
                        f"onebot11/account({self.account.route['account']}).group({target['group']}).file({target['file']})", filedata,
                        timedelta(minutes=5),
                    )
                    return filedata
            for _folder in res2["folders"]:
                _folderdata = folder_parse(_folder, data)
                if _folderdata.id == target["file"]:
                    await cache.set(
                        f"onebot11/account({self.account.route['account']}).group({target['group']}).file({target['file']})", _folderdata,
                        timedelta(minutes=5),
                    )
                    return _folderdata
                return await step(_folderdata)
            raise RuntimeError(f"File {target} not found.")

        res1 = await self.account.connection.call(
            "get_group_root_files",
            {
                "group_id": int(target["group"]),
            },
        )
        if not res1:
            raise RuntimeError(f"File {target} not found.")
        for file in res1["files"]:
            _res = await self.account.connection.call(
                "get_group_file_url",
                {
                    "group_id": int(target["group"]),
                    "file_id": file["file_id"],
                    "busid": file["busid"],
                },
            )
            filedata = file_parse(file, _res["url"] if _res else "")
            if filedata.id == target["file"]:
                await cache.set(
                    f"onebot11/account({self.account.route['account']}).group({target['group']}).file({target['file']})", filedata,
                    timedelta(minutes=5),
                )
                return filedata

        for folder in res1["folders"]:
            folderdata = folder_parse(folder)
            if folderdata.id == target["file"]:
                await cache.set(
                    f"onebot11/account({self.account.route['account']}).group({target['group']}).file({target['file']})", folderdata,
                    timedelta(minutes=5),
                )
                return folderdata
            return await step(folderdata)

        raise RuntimeError(f"File {target} not found.")


    @m.entity(FileCapability.upload, target="land.group")
    async def upload_group_file(
        self,
        target: Selector,
        name: str,
        file: bytes | IO[bytes] | os.PathLike,
        path: str | None = None,
    ) -> None:
        _name = name or ""
        _path = path or ""
        if "/" in _path and not _name:
            _path, _name = _path.rsplit("/", 1)

        if isinstance(file, os.PathLike):
            await self.account.connection.call(
                "upload_group_file",
                {
                    "group_id": int(target["group"]),
                    "file": Path(file).resolve().as_posix(),
                    "name": _name,
                    "folder": _path,
                },
            )
        else:
            with NamedTemporaryFile() as temp:
                temp.write(file)  # type: ignore
                temp.flush()
                await self.account.connection.call(
                    "upload_group_file",
                    {
                        "group_id": int(target["group"]),
                        "file": temp.name,
                        "name": _name,
                        "folder": _path,
                    },
                )

    @m.entity(FileCapability.upload, target="land.friend")
    async def upload_private_file(
        self,
        target: Selector,
        name: str,
        file: bytes | IO[bytes] | os.PathLike,
        path: str | None = None,
    ) -> None:
        _name = name or ""
        _path = path or ""
        if "/" in _path and not _name:
            _path, _name = _path.rsplit("/", 1)

        if isinstance(file, os.PathLike):
            await self.account.connection.call(
                "upload_private_file",
                {
                    "user_id": int(target["friend"]),
                    "file": Path(file).resolve().as_posix(),
                    "name": _name,
                },
            )
        else:
            with NamedTemporaryFile() as temp:
                temp.write(file)  # type: ignore
                temp.flush()
                await self.account.connection.call(
                    "upload_group_file",
                    {
                        "user_id": int(target["friend"]),
                        "file": temp.name,
                        "name": _name,
                    },
                )

    @m.entity(FileDirectoryCapability.create, target="land.group")
    async def create_directory(self, target: Selector, name: str, parent: str | None = None):
        await self.account.connection.call(
            "create_group_file_folder",
            {
                "group_id": int(target["group"]),
                "parent_id": "/",
                "name": name,
            },
        )

    @m.entity(FileCapability.delete, file="land.group.file")
    async def delete_file(self, file: Selector, busid: int | None = None) -> None:
        await self.account.connection.call(
            "delete_group_file",
            {
                "file_id": file["file"],
                "group_id": int(file["group"]),
                "busid": busid,
            },
        )

    @m.entity(FileDirectoryCapability.delete, file="land.group.file")
    async def delete_folder(self, file: Selector) -> None:
        await self.account.connection.call(
            "delete_group_folder",
            {
                "folder_id": file["file"],
                "group_id": int(file["group"]),
            },
        )
