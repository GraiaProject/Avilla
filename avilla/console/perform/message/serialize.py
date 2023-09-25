from __future__ import annotations

from dataclasses import asdict
from typing import TYPE_CHECKING

from nonechat.message import Emoji as CslEmoji
from nonechat.message import Markdown as CslMarkdown
from nonechat.message import Markup as CslMarkup
from nonechat.message import Text as CslText

from avilla.console.capability import ConsoleCapability
from avilla.console.element import Markdown, Markup
from avilla.core.elements import Face, Text
from avilla.core.ryanvk.collector.account import AccountCollector

if TYPE_CHECKING:
    from ...account import ConsoleAccount  # noqa
    from ...protocol import ConsoleProtocol  # noqa


class ConsoleMessageSerializePerform((m := AccountCollector["ConsoleProtocol", "ConsoleAccount"]())._):
    m.namespace = "avilla.protocol/console::message"
    m.identify = "serialize"

    # LINK: https://github.com/microsoft/pyright/issues/5409

    @m.entity(ConsoleCapability.serialize_element, element=Text)
    async def text(self, element: Text):
        return CslText(element.text)

    @m.entity(ConsoleCapability.serialize_element, element=Face)
    async def emoji(self, element: Face):
        return CslEmoji(element.id)

    @m.entity(ConsoleCapability.serialize_element, element=Markup)
    async def markup(self, element: Markup):
        return CslMarkup(**asdict(element))

    @m.entity(ConsoleCapability.serialize_element, element=Markdown)
    async def markdown(self, element: Markdown):
        return CslMarkdown(**asdict(element))
