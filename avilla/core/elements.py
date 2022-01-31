from pathlib import Path
from typing import Optional, Union

from avilla.core.message import Element
from avilla.core.selectors import entity as entity_selector
from avilla.core.selectors import resource as resource_selector


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

    target: entity_selector

    def __init__(self, target: entity_selector) -> None:
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


class Image(Element):
    source: resource_selector

    def __init__(self, source: Union[resource_selector, Path, str]):
        if isinstance(source, Path):
            source = resource_selector.file[str(source.absolute())]
        elif isinstance(source, str):
            source = resource_selector.file[source]
        self.source = source

    def asDisplay(self) -> str:
        return "[$Image]"


class Voice(Element):
    source: resource_selector

    def __init__(self, source: resource_selector):
        self.source = source

    def asDisplay(self) -> str:
        return "[$Voice]"


class Video(Element):
    source: resource_selector

    def __init__(self, source: resource_selector):
        self.source = source

    def asDisplay(self) -> str:
        return "[$Video]"
