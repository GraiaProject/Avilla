from __future__ import annotations

from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from . import MessageChain


class Element:
    _chain_class: type[MessageChain]

    def __str__(self) -> str:
        return ""

    def __add__(self: Element, content: MessageChain | list[Element] | Element | str) -> MessageChain:
        from . import MessageChain

        if isinstance(content, str):
            content = [self._chain_class._text_class(content)]
        if isinstance(content, Element):
            content = [content]
        if isinstance(content, MessageChain):
            content = content.content
        return self._chain_class(content + [self])

    def __radd__(self: Element, content: MessageChain | list[Element] | Element | str) -> MessageChain:
        from . import MessageChain
        
        if isinstance(content, str):
            content = [self._chain_class._text_class(content)]
        if isinstance(content, Element):
            content = [content]
        if isinstance(content, MessageChain):
            content = content.content
        return self._chain_class([self] + content)


class Text(Element):
    text: str
    style: str | None

    def __init__(self, text: str, style: str | None = None) -> None:
        """实例化一个 Text 消息元素, 用于承载消息中的文字.

        Args:
            text (str): 元素所包含的文字
            style (Optional[str]): 默认为空, 文字的样式
        """
        self.text = text
        self.style = style

    def __str__(self) -> str:
        return self.text

    def __repr__(self) -> str:
        return f"Text(text={self.text}{f', style={self.style}' if self.style else ''})"


class Unknown(Element):
    type: str
    raw_data: Any

    def __init__(self, type: str, raw_data: Any) -> None:
        self.type = type
        self.raw_data = raw_data

    def __str__(self) -> str:
        return f"[$Unknown:type={self.type}]"

    def __repr__(self) -> str:
        return f"Unknown(type={self.type}, raw=<{self.raw_data.__class__.__name__}>)"
