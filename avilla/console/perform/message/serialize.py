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
from flywheel import global_collect

if TYPE_CHECKING:
    from ...account import ConsoleAccount  # noqa
    from ...protocol import ConsoleProtocol  # noqa


@global_collect
@ConsoleCapability.serialize_element.impl(element=Text)
async def text(element: Text):
    return CslText(element.text)


@global_collect
@ConsoleCapability.serialize_element.impl(element=Face)
async def emoji(element: Face):
    return CslEmoji(element.id)


@global_collect
@ConsoleCapability.serialize_element.impl(element=Markup)
async def markup(element: Markup):
    return CslMarkup(**asdict(element))


@global_collect
@ConsoleCapability.serialize_element.impl(element=Markdown)
async def markdown(element: Markdown):
    return CslMarkdown(**asdict(element))
