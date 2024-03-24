from __future__ import annotations

from dataclasses import asdict

from nonechat.message import Emoji as CslEmoji
from nonechat.message import Markdown as CslMarkdown
from nonechat.message import Markup as CslMarkup
from nonechat.message import Text as CslText

from avilla.console.capability import ConsoleCapability
from avilla.console.element import Markdown, Markup
from avilla.core.elements import Face, Text
from flywheel import global_collect

@global_collect
@ConsoleCapability.deserialize_element.impl(element=CslText)
async def text(element: CslText) -> Text:
    return Text(element.text)


@global_collect
@ConsoleCapability.deserialize_element.impl(element=CslEmoji)
async def emoji(element: CslEmoji) -> Face:
    return Face(element.name)


@global_collect
@ConsoleCapability.deserialize_element.impl(element=CslMarkup)
async def markup(element: CslMarkup) -> Markup:
    return Markup(**asdict(element))


@global_collect
@ConsoleCapability.deserialize_element.impl(element=CslMarkdown)
async def markdown(element: CslMarkdown) -> Markdown:
    return Markdown(**asdict(element))
