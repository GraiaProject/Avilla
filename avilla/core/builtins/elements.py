from pathlib import Path
from typing import Optional

from avilla.core.message.element import Element
from avilla.core.provider import Provider, RawProvider
from avilla.core.resource import Resource


class Text(Element):
    text: str
    style: Optional[str]

    def __init__(self, text: str, style: str = None) -> None:
        """实例化一个 Text 消息元素, 用于承载消息中的文字.

        Args:
            text (str): 元素所包含的文字
        """
        self.text = text
        self.style = style

    def asDisplay(self) -> str:
        return self.text


class Notice(Element):
    """该消息元素用于承载消息中用于提醒/呼唤特定用户的部分."""

    target: str

    def __init__(self, target: str) -> None:
        """实例化一个 Notice 消息元素, 用于承载消息中用于提醒/呼唤特定用户的部分.

        Args:
            target (str): 需要提醒/呼唤的特定用户的 ID.
        """
        self.target = target

    def asDisplay(self) -> str:
        return f"[$Notice:target={self.target}]"


class NoticeAll(Element):
    "该消息元素用于群组中的管理员提醒群组中的所有成员"

    def __init__(self) -> None:
        super().__init__()

    def asDisplay(self) -> str:
        return "[$NoticeAll]"


class Image(Element, Resource):
    def __init__(self, provider: Provider):
        self.provider = provider

    @classmethod
    def fromLocalFile(cls, path: Path):
        data = path.read_bytes()
        return cls(RawProvider(data))

    def asDisplay(self) -> str:
        return "[$Image]"


class Quote(Element):
    id: str

    def __init__(self, id: str) -> None:
        self.id = id

    def asDisplay(self) -> str:
        return f"[$Quote:id={self.id}]"


class Voice(Element, Resource):
    def __init__(self, provider: Provider):
        self.provider = provider

    @classmethod
    def fromLocalFile(cls, path: Path):
        data = path.read_bytes()
        return cls(RawProvider(data))

    def asDisplay(self) -> str:
        return "[$Voice]"


class Video(Element, Resource):
    def __init__(self, provider: Provider):
        self.provider = provider

    @classmethod
    def fromLocalFile(cls, path: Path):
        data = path.read_bytes()
        return cls(RawProvider(data))

    def asDisplay(self) -> str:
        return "[$Video]"
