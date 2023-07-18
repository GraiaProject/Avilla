from typing import Iterator, Sequence, Union, overload

from rich.console import Console, ConsoleOptions, RenderResult
from rich.measure import Measurement, measure_renderables
from rich.segment import Segment

from graia.amnesia.message.element import Element

from .element import ConsoleElement, Markdown


class ConsoleMessage(Sequence[ConsoleElement]):
    content: list[ConsoleElement]

    @overload
    def __getitem__(self, index: int) -> Element:
        ...

    @overload
    def __getitem__(self, index: slice) -> Sequence[Element]:
        ...

    def __getitem__(self, index: Union[int, slice]) -> Union[Element, Sequence[Element]]:
        return self.content[index]

    def __len__(self) -> int:
        return len(self.content)

    def __init__(self, elements: list[ConsoleElement]):
        """从传入的序列(可以是元组 tuple, 也可以是列表 list) 创建消息链.
        Args:
            elements (list[T]): 包含且仅包含消息元素的序列
        Returns:
            MessageChain: 以传入的序列作为所承载消息的消息链
        """
        self.content = elements

    def __iter__(self) -> Iterator[ConsoleElement]:
        yield from self.content

    def __reversed__(self) -> Iterator[ConsoleElement]:
        yield from reversed(self.content)

    def __rich_console__(self, console: "Console", options: "ConsoleOptions") -> "RenderResult":
        yield from self
        if self.content and not isinstance(self.content[-1], Markdown):
            yield Segment("\n")

    def __rich_measure__(self, console: "Console", options: "ConsoleOptions") -> Measurement:
        return measure_renderables(console, options, self)
