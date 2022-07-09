from __future__ import annotations

from pathlib import Path
from typing import Any

from graia.amnesia.message import Element
from graia.amnesia.message.element import Text as Text

from avilla.core.resource import Resource
from avilla.core.resource.local import LocalFileResource
from avilla.core.utilles.selector import Selector


class Notice(Element):
    """该消息元素用于承载消息中用于提醒/呼唤特定用户的部分."""

    target: Selector

    def __init__(self, target: Selector) -> None:
        """实例化一个 Notice 消息元素, 用于承载消息中用于提醒/呼唤特定用户的部分.

        Args:
            target (str): 需要提醒/呼唤的特定用户的 ID.
        """

        self.target = target

    def __str__(self) -> str:
        return f"[$Notice:target={self.target}]"


class NoticeAll(Element):
    "该消息元素用于群组中的管理员提醒群组中的所有成员"

    def __init__(self) -> None:
        super().__init__()

    def __str__(self) -> str:
        return "[$NoticeAll]"


class Image(Element):
    resource: Resource[bytes]

    def __init__(self, resource: Resource[bytes] | Path | str):
        if isinstance(resource, Path):
            resource = LocalFileResource(resource)
        elif isinstance(resource, str):
            resource = LocalFileResource(Path(resource))
        self.resource = resource

    def __str__(self) -> str:
        return "[$Image]"


class Audio(Element):
    resource: Resource[bytes]

    def __init__(self, resource: Resource[bytes] | Path | str):
        if isinstance(resource, Path):
            resource = LocalFileResource(resource)
        elif isinstance(resource, str):
            resource = LocalFileResource(Path(resource))
        self.resource = resource

    def __str__(self) -> str:
        return "[$Audio]"


class Video(Element):
    resource: Resource[bytes]

    def __init__(self, resource: Resource[bytes] | Path | str):
        if isinstance(resource, Path):
            resource = LocalFileResource(resource)
        elif isinstance(resource, str):
            resource = LocalFileResource(Path(resource))
        self.resource = resource

    def __str__(self) -> str:
        return "[$Video]"


class Unknown(Element):
    type: str
    raw_data: Any

    def __init__(self, type: str, raw_data: Any) -> None:
        self.type = type
        self.raw_data = raw_data

    def __str__(self) -> str:
        return f"[$Unknown:type={self.type}]"
