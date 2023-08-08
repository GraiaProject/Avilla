from __future__ import annotations

from dataclasses import asdict
from typing import TYPE_CHECKING

from nonechat.message import Element
from nonechat.message import Emoji as CslEmoji
from nonechat.message import Markdown as CslMarkdown
from nonechat.message import Markup as CslMarkup
from nonechat.message import Text as CslText

from avilla.console.element import Emoji, Markdown, Markup
from avilla.core.elements import Text
from avilla.core.ryanvk.collector.account import AccountCollector
from avilla.core.ryanvk.descriptor.message.serialize import MessageSerialize

if TYPE_CHECKING:
    from ...account import ConsoleAccount  # noqa
    from ...protocol import ConsoleProtocol  # noqa

ConsoleMessageSerialize = MessageSerialize[Element]


class ConsoleMessageSerializePerform((m := AccountCollector["ConsoleProtocol", "ConsoleAccount"]())._):
    m.post_applying = True

    # LINK: https://github.com/microsoft/pyright/issues/5409

    @m.entity(ConsoleMessageSerialize, Text)
    async def text(self, element: Text) -> Element:
        return CslText(element.text)

    @m.entity(ConsoleMessageSerialize, Emoji)
    async def emoji(self, element: Emoji) -> Element:
        return CslEmoji(element.name)

    @m.entity(ConsoleMessageSerialize, Markup)
    async def markup(self, element: Markup) -> Element:
        return CslMarkup(**asdict(element))

    @m.entity(ConsoleMessageSerialize, Markdown)
    async def markdown(self, element: Markdown) -> Element:
        return CslMarkdown(**asdict(element))
