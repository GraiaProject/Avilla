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
from avilla.core.ryanvk.collector.application import ApplicationCollector
from avilla.core.ryanvk.descriptor.message.deserialize import MessageDeserialize

ConsoleMessageDeserialize = MessageDeserialize[Element]


class ConsoleMessageDeserializePerform((m := ApplicationCollector())._):
    m.post_applying = True

    # LINK: https://github.com/microsoft/pyright/issues/5409

    @m.entity(ConsoleMessageDeserialize, "Text")
    async def text(self, element: Element) -> Text:
        if TYPE_CHECKING:
            assert isinstance(element, CslText)
        return Text(element.text)

    @m.entity(ConsoleMessageDeserialize, "Emoji")
    async def emoji(self, element: Element) -> Emoji:
        if TYPE_CHECKING:
            assert isinstance(element, CslEmoji)
        return Emoji(element.name)

    @m.entity(ConsoleMessageDeserialize, "Markup")
    async def markup(self, element: Element) -> Markup:
        if TYPE_CHECKING:
            assert isinstance(element, CslMarkup)
        return Markup(**asdict(element))

    @m.entity(ConsoleMessageDeserialize, "Markdown")
    async def markdown(self, element: Element) -> Markdown:
        if TYPE_CHECKING:
            assert isinstance(element, CslMarkdown)
        return Markdown(**asdict(element))
