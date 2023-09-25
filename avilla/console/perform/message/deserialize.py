from __future__ import annotations

from dataclasses import asdict

from nonechat.message import Emoji as CslEmoji
from nonechat.message import Markdown as CslMarkdown
from nonechat.message import Markup as CslMarkup
from nonechat.message import Text as CslText

from avilla.console.capability import ConsoleCapability
from avilla.console.element import Markdown, Markup
from avilla.core.elements import Text, Face
from avilla.core.ryanvk.collector.application import ApplicationCollector


class ConsoleMessageDeserializePerform((m := ApplicationCollector())._):
    m.namespace = "avilla.protocol/console::message"
    m.identify = "deserialize"

    # LINK: https://github.com/microsoft/pyright/issues/5409

    @m.entity(ConsoleCapability.deserialize_element, element=CslText)
    async def text(self, element: CslText) -> Text:
        return Text(element.text)

    @m.entity(ConsoleCapability.deserialize_element, element=CslEmoji)
    async def emoji(self, element: CslEmoji) -> Face:
        return Face(element.name)

    @m.entity(ConsoleCapability.deserialize_element, element=CslMarkup)
    async def markup(self, element: CslMarkup) -> Markup:
        return Markup(**asdict(element))

    @m.entity(ConsoleCapability.deserialize_element, element=CslMarkdown)
    async def markdown(self, element: CslMarkdown) -> Markdown:
        return Markdown(**asdict(element))
