from __future__ import annotations

from datetime import timedelta
from typing import TYPE_CHECKING, Callable

from graia.amnesia.builtins.memcache import Memcache, MemcacheService

from avilla.core.ryanvk.collector.account import AccountCollector
from avilla.core.selector import Selector
from avilla.onebot.v11.utils import file_parse, folder_parse

from avilla.core.builtins.capability import CoreCapability

if TYPE_CHECKING:
    from avilla.onebot.v11.account import OneBot11Account  # noqa
    from avilla.onebot.v11.protocol import OneBot11Protocol  # noqa


class OneBot11FileQueryPerform((m := AccountCollector["OneBot11Protocol", "OneBot11Account"]())._):
    m.namespace = "avilla.protocol/onebot11::query"
    m.identify = "file"

    @CoreCapability.query.collect(m, "file", "land.group")
    async def query_group_file(self, predicate: Callable[[str, str], bool] | str, previous: Selector):
        cache: Memcache = self.protocol.avilla.launch_manager.get_component(MemcacheService).cache

        res1 = await self.account.connection.call(
            "get_group_root_files",
            {
                "group_id": int(previous["group"]),
            },
        )
        if not res1:
            raise RuntimeError(f"Cant find file in {previous}")
        for file in res1["files"]:
            _res = await self.account.connection.call(
                "get_group_file_url",
                {
                    "group_id": int(previous["group"]),
                    "file_id": file["file_id"],
                    "busid": file["busid"],
                },
            )
            filedata = file_parse(file, _res["url"] if _res else "")
            await cache.set(
                f"onebot11/account({self.account.route['account']}).group({previous['group']}).file({filedata.id})",
                filedata,
                timedelta(minutes=5),
            )
            if callable(predicate) and predicate("file", filedata.id) or filedata.id == predicate:
                yield Selector().land(self.account.route["land"]).group(previous["group"]).file(filedata.id)

        for folder in res1["folders"]:
            folderdata = folder_parse(folder)
            await cache.set(
                f"onebot11/account({self.account.route['account']}).group({previous['group']}).file({folderdata.id})",
                folderdata,
                timedelta(minutes=5),
            )
            if callable(predicate) and predicate("file", folderdata.id) or folderdata.id == predicate:
                yield Selector().land(self.account.route["land"]).group(previous["group"]).file(folderdata.id)
            res2 = await self.account.connection.call(
                "get_group_files_by_folder",
                {
                    "group_id": int(previous["group"]),
                    "folder_id": folderdata.id,
                },
            )
            if not res2:
                raise RuntimeError(f"Cant find file in {previous}")
            for file in res2["files"]:
                _res = await self.account.connection.call(
                    "get_group_file_url",
                    {
                        "group_id": int(previous["group"]),
                        "file_id": file["file_id"],
                        "busid": file["busid"],
                    },
                )
                filedata = file_parse(file, _res["url"] if _res else "", folderdata)
                await cache.set(
                    f"onebot11/account({self.account.route['account']}).group({previous['group']}).file({filedata.id})",
                    filedata,
                    timedelta(minutes=5),
                )
                if callable(predicate) and predicate("file", filedata.id) or filedata.id == predicate:
                    yield Selector().land(self.account.route["land"]).group(previous["group"]).file(filedata.id)
            for _folder in res2["folders"]:
                _folderdata = folder_parse(_folder, folderdata)
                await cache.set(
                    f"onebot11/account({self.account.route['account']}).group({previous['group']}).file({_folderdata.id})",
                    _folderdata,
                    timedelta(minutes=5),
                )
                if callable(predicate) and predicate("file", _folderdata.id) or _folderdata.id == predicate:
                    yield Selector().land(self.account.route["land"]).group(previous["group"]).file(_folderdata.id)
