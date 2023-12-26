from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

from graia.amnesia.message import Element
from graia.amnesia.message import Text as Text  # noqa

from avilla.core.resource import LocalFileResource, Resource
from avilla.core.selector import Selector


class Notice(Element):
    """该消息元素用于承载消息中用于提醒/呼唤特定用户的部分."""

    target: Selector
    display: str | None

    def __init__(self, target: Selector, display: str | None = None) -> None:
        """实例化一个 Notice 消息元素，用于承载消息中用于提醒/呼唤特定用户的部分。

        Args:
            target (str): 需要提醒/呼唤的特定用户的 ID.
            display (str, optional): 需要提醒/呼唤的特定用户的显示名称. Defaults to None.
        """

        self.target = target
        self.display = display

    def __str__(self) -> str:
        return "[$Notice]"

    def __repr__(self) -> str:
        return f"[$Notice:target={self.target}]"


class NoticeAll(Element):
    """该消息元素用于群组中的管理员提醒群组中的所有成员"""

    def __init__(self) -> None:
        super().__init__()

    def __str__(self) -> str:
        return "[$NoticeAll]"


class Picture(Element):
    resource: Resource[bytes]

    def __init__(self, resource: Resource[bytes] | Path | str):
        if isinstance(resource, Path):
            resource = LocalFileResource(resource)
        elif isinstance(resource, str):
            resource = LocalFileResource(Path(resource))
        self.resource = resource

    def __str__(self) -> str:
        return "[$Picture]"

    def __repr__(self):
        return f"[$Picture:resource={self.resource.to_selector()}]"


class Audio(Element):
    resource: Resource[bytes]
    duration: int

    def __init__(self, resource: Resource[bytes] | Path | str, duration: int = -1):
        if isinstance(resource, Path):
            resource = LocalFileResource(resource)
        elif isinstance(resource, str):
            resource = LocalFileResource(Path(resource))
        self.resource = resource
        self.duration = duration

    def __str__(self) -> str:
        return "[$Audio]"

    def __repr__(self):
        return f"[$Audio:resource={self.resource.to_selector()}]"


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

    def __repr__(self):
        return f"[$Video:resource={self.resource.to_selector()}]"


class File(Element):
    resource: Resource[bytes]

    def __init__(self, resource: Resource[bytes] | Path | str):
        if isinstance(resource, Path):
            resource = LocalFileResource(resource)
        elif isinstance(resource, str):
            resource = LocalFileResource(Path(resource))
        self.resource = resource

    def __str__(self) -> str:
        return "[$File]"

    def __repr__(self) -> str:
        return f"[$File:resource={self.resource.to_selector()}]"


@dataclass
class Reference(Element):
    message: Selector
    slice: tuple[int, int] | None = None

    def __str__(self):
        return f"[$Reference:id={self.message}]"


@dataclass
class Face(Element):
    id: str
    name: str | None = None

    def __str__(self) -> str:
        return f"[Face:id={self.id};name={self.name}]"


class Unknown(Element):
    type: str
    raw_data: Any

    def __init__(self, type: str, raw_data: Any) -> None:
        self.type = type
        self.raw_data = raw_data

    def __str__(self) -> str:
        return f"[$Unknown:type={self.type}]"
