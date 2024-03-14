from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime

from avilla.core.metadata import Metadata
from avilla.core.selector import Selector


@dataclass
class DownloadInfo:
    sha1: str
    md5: str
    url: str


@dataclass
class FileData(Metadata):
    id: str
    scene: Selector
    name: str
    parent: FileData | None
    is_file: bool
    is_dir: bool
    upload_time: datetime | None
    modify_time: datetime | None
    download_info: DownloadInfo | None

    def to_selector(self):
        return self.scene.file(self.id)

    @classmethod
    def parse(cls, raw: dict):
        return cls(
            raw["id"],
            Selector().land("qq").group(str(raw["contact"]["id"])),
            raw["name"],
            cls.parse(raw["parent"]) if raw["parent"] else None,
            raw["isFile"],
            raw["isDirectory"],
            datetime.fromtimestamp(raw["uploadTime"]) if raw["uploadTime"] else None,
            datetime.fromtimestamp(raw["lastModifyTime"]) if raw["lastModifyTime"] else None,
            DownloadInfo(
                raw["downloadInfo"]["sha1"],
                raw["downloadInfo"]["md5"],
                raw["downloadInfo"]["url"],
            )
            if raw["downloadInfo"]
            else None,
        )
