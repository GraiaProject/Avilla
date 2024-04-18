from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime

from avilla.core.metadata import Metadata
from avilla.core.selector import Selector


@dataclass
class DownloadInfo:
    times: int
    url: str
    sha1: str | None = None
    md5: str | None = None


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
    busid: int | None = None
    size: int | None = None

    def to_selector(self):
        return self.scene.file(self.id)


