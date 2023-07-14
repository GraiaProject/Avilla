from __future__ import annotations

from typing import TYPE_CHECKING

from avilla.core.elements import Text
from avilla.core.ryanvk.collector.account import AccountCollector
from avilla.core.ryanvk.descriptor.message.serialize import MessageSerialize

from avilla.console.element import Text as RichText, Emoji, Markup, Markdown, ConsoleElement

if TYPE_CHECKING:
    from ...account import ConsoleAccount  # noqa
    from ...protocol import ConsoleProtocol  # noqa

ConsoleMessageSerialize = MessageSerialize[ConsoleElement]


class ConsoleMessageSerializePerform((m := AccountCollector["ConsoleProtocol", "ConsoleAccount"]())._):
    m.post_applying = True

    # LINK: https://github.com/microsoft/pyright/issues/5409

    @ConsoleMessageSerialize.collect(m, Text)
    async def text(self, element: Text) -> ConsoleElement:
        return RichText(element.text)

    @ConsoleMessageSerialize.collect(m, Emoji)
    async def emoji(self, element: Emoji) -> ConsoleElement:
        return element

    @ConsoleMessageSerialize.collect(m, Markup)
    async def markup(self, element: Markup) -> ConsoleElement:
        return element

    @ConsoleMessageSerialize.collect(m, Markdown)
    async def markdown(self, element: Markdown) -> ConsoleElement:
        return element
