import os
from pathlib import Path

from graia.amnesia.message import MessageChain

from avilla.core import Audio, Avilla, Context, MessageReceived, Text
from avilla.standard.core.message import MessageSent
from avilla.standard.telegram.constants import DiceEmoji
from avilla.standard.telegram.elements import Dice, Picture, Video, Voice
from avilla.standard.telegram.event import (
    ForumTopicClosed,
    ForumTopicCreated,
    ForumTopicEdited,
    ForumTopicReopened,
    GeneralForumTopicHidden,
    GeneralForumTopicUnhidden,
)
from avilla.telegram.protocol import TelegramBotConfig, TelegramProtocol

config = TelegramBotConfig(os.environ["TELEGRAM_TOKEN"], reformat=False)
avilla = Avilla(message_cache_size=0)
avilla.apply_protocols(TelegramProtocol().configure(config))


@avilla.listen(MessageReceived)
async def on_message_received(cx: Context, event: MessageReceived, msg: MessageChain):
    # print(repr(event))
    print(f"{msg = }")
    await cx.scene.send_message(
        # MessageChain(
        #     [
        #         # Dice(DiceEmoji.SLOT_MACHINE),
        #         # Picture(Path("test.jpg"), has_spoiler=False),
        #         # Text("Hello, Avilla!"),
        #         # Video(Path("test.mp4"), has_spoiler=True),
        #         # Text("Hello, Avilla!"),
        #         Voice(Path("test.mp3")),
        #     ]
        # ),
        msg,
        reply=event.message,
    )


# @avilla.listen(ForumTopicCreated)
# async def forum_topic_created(cx: Context):
#     await cx.scene.send_message(MessageChain([Text("Event: ForumTopicCreated")]))
#
#
# @avilla.listen(ForumTopicClosed)
# async def forum_topic_closed(cx: Context):
#     await cx.scene.send_message(MessageChain([Text("Event: ForumTopicClosed")]))
#
#
# @avilla.listen(ForumTopicEdited)
# async def forum_topic_edited(cx: Context):
#     await cx.scene.send_message(MessageChain([Text("Event: ForumTopicEdited")]))
#
#
# @avilla.listen(ForumTopicReopened)
# async def forum_topic_reopened(cx: Context):
#     await cx.scene.send_message(MessageChain([Text("Event: ForumTopicReopened")]))
#
#
# @avilla.listen(GeneralForumTopicHidden)
# async def general_forum_topic_hidden(cx: Context):
#     await cx.scene.send_message(MessageChain([Text("Event: GeneralForumTopicHidden")]))
#
#
# @avilla.listen(GeneralForumTopicUnhidden)
# async def general_forum_topic_unhidden(cx: Context):
#     await cx.scene.send_message(MessageChain([Text("Event: GeneralForumTopicUnhidden")]))


@avilla.listen(MessageSent)
async def on_message_sent(event: MessageSent):
    print(repr(event))


avilla.launch()
