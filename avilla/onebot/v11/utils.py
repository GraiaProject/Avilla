from __future__ import annotations

from datetime import datetime
from avilla.standard.core.file.metadata import DownloadInfo, FileData

from avilla.core.selector import Selector


def file_parse(raw: dict, url: str, parent: FileData | None = None):
    return FileData(
        raw["file_id"],
        Selector().land("qq").group(str(raw["group_id"])),
        raw["file_name"],
        parent=parent,
        is_file=True,
        is_dir=False,
        upload_time=datetime.fromtimestamp(raw["upload_time"]) if raw["upload_time"] else None,
        modify_time=datetime.fromtimestamp(raw["modify_time"]) if raw["modify_time"] else None,
        download_info=DownloadInfo(
            raw["download_times"],
            url,
        ),
        busid=raw["busid"]
    )


def folder_parse(raw: dict, parent: FileData | None = None):
    return FileData(
        raw["folder_id"],
        Selector().land("qq").group(str(raw["group_id"])),
        raw["folder_name"],
        parent=parent,
        is_file=False,
        is_dir=True,
        upload_time=datetime.fromtimestamp(raw["create_time"]) if raw["create_time"] else None,
        modify_time=None,
        download_info=None,
    )