from __future__ import annotations

from typing import TYPE_CHECKING

from avilla.core.elements import Text as BaseText
from avilla.core.ryanvk.collector.account import AccountCollector
from avilla.core.ryanvk.descriptor.message.deserialize import MessageDeserialize

from avilla.console.element import ConsoleElement, Emoji, Markdown, Markup, Text

if TYPE_CHECKING:
    from ...account import ConsoleAccount  # noqa
    from ...protocol import ConsoleProtocol  # noqa

ConsoleMessageDeserialize = MessageDeserialize[ConsoleElement]


class ConsoleMessageDeserializePerform(
    (m := AccountCollector["ConsoleProtocol", "ConsoleAccount"]())._
):
    m.post_applying = True

    # LINK: https://github.com/microsoft/pyright/issues/5409

    @ConsoleMessageDeserialize.collect(m, "Text")
    async def text(self, element: ConsoleElement) -> BaseText:
        if TYPE_CHECKING:
            assert isinstance(element, Text)
        return BaseText(element.text)

    @ConsoleMessageDeserialize.collect(m, "Emoji")
    async def emoji(self, element: ConsoleElement) -> Emoji:
        if TYPE_CHECKING:
            assert isinstance(element, Emoji)
        return element

    @ConsoleMessageDeserialize.collect(m, "Markup")
    async def markup(self, element: ConsoleElement) -> Markup:
        if TYPE_CHECKING:
            assert isinstance(element, Markup)
        return element

    @ConsoleMessageDeserialize.collect(m, "Markdown")
    async def markdown(self, element: ConsoleElement) -> Markdown:
        if TYPE_CHECKING:
            assert isinstance(element, Markdown)
        return element
