from datetime import datetime
from avilla.standard.core.file.metadata import DownloadInfo, FileData

from avilla.core.selector import Selector


def filedata_parse(raw: dict):
    return FileData(
        raw["id"],
        Selector().land("qq").group(str(raw["contact"]["id"])),
        raw["name"],
        filedata_parse(raw["parent"]) if raw["parent"] else None,
        raw["isFile"],
        raw["isDirectory"],
        datetime.fromtimestamp(raw["uploadTime"]) if raw["uploadTime"] else None,
        datetime.fromtimestamp(raw["lastModifyTime"]) if raw["lastModifyTime"] else None,
        DownloadInfo(
            raw["downloadInfo"].get("downloadTimes", raw["downloadTimes"]),
            raw["downloadInfo"]["url"],
            raw["downloadInfo"]["sha1"],
            raw["downloadInfo"]["md5"],
        )
        if raw["downloadInfo"]
        else None,
    )
