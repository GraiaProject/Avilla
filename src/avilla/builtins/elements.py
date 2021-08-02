from typing import Callable, NoReturn

from pathlib import Path

from avilla.message.element import Element
from avilla.resource import Resource
from avilla.provider import Provider, RawProvider


class PlainText(Element):
    text: str

    def __init__(self, text: str) -> NoReturn:
        """实例化一个 Plain 消息元素, 用于承载消息中的文字.

        Args:
            text (str): 元素所包含的文字
        """
        super().__init__(text=text)

    def asDisplay(self) -> str:
        return self.text


class Notice(Element):
    """该消息元素用于承载消息中用于提醒/呼唤特定用户的部分."""

    target: str

    def __init__(self, target: str, **kwargs) -> None:
        """实例化一个 Notice 消息元素, 用于承载消息中用于提醒/呼唤特定用户的部分.

        Args:
            target (str): 需要提醒/呼唤的特定用户的 ID.
        """
        super().__init__(target=target, **kwargs)

    def asDisplay(self) -> str:
        return f"[$Notice:target={self.target}]"


class NoticeAll(Element):
    "该消息元素用于群组中的管理员提醒群组中的所有成员"

    def __init__(self) -> None:
        super().__init__()

    def asDisplay(self) -> str:
        return "[$NoticeAll]"


class Image(Element, Resource[Provider[bytes]]):
    provider: Callable[[], bytes]

    def __init__(self, provider: Provider):
        super().__init__(provider=provider)

    @classmethod
    def fromLocalFile(cls, path: Path):
        data = path.read_bytes()
        return cls(RawProvider(data))

    def asDisplay(self) -> str:
        return "[$Image]"

    class Config:
        arbitrary_types_allowed = True


class Quote(Element):
    id: str

    def asDisplay(self) -> str:
        return f"[$Quote:id={self.id}]"


class Voice(Element, Resource[Provider[bytes]]):
    provider: Callable[[], bytes]

    def __init__(self, provider: Provider):
        super().__init__(provider=provider)

    @classmethod
    def fromLocalFile(cls, path: Path):
        data = path.read_bytes()
        return cls(RawProvider(data))

    class Config:
        arbitrary_types_allowed = True

    def asDisplay(self) -> str:
        return "[$Voice]"


class Video(Element, Resource[Provider[bytes]]):
    provider: Callable[[], bytes]

    def __init__(self, provider: Provider):
        super().__init__(provider=provider)

    @classmethod
    def fromLocalFile(cls, path: Path):
        data = path.read_bytes()
        return cls(RawProvider(data))

    def asDisplay(self) -> str:
        return "[$Video]"

    class Config:
        arbitrary_types_allowed = True
