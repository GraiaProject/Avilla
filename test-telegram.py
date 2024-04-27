import asyncio
import os

from graia.amnesia.message import MessageChain
from loguru import logger

from avilla.core import Avilla, Context, MessageReceived
from avilla.standard.core.message import MessageEdit, MessageSent
from avilla.standard.core.profile import Avatar
from avilla.telegram.protocol import TelegramLongPollingConfig, TelegramProtocol

config = TelegramLongPollingConfig(os.environ["TELEGRAM_TOKEN"])
avilla = Avilla(message_cache_size=0)
avilla.apply_protocols(TelegramProtocol().configure(config))


@avilla.listen(MessageReceived)
async def on_message_received(cx: Context, event: MessageReceived, message: MessageChain):
    # print(repr(event))
    logger.debug(f"{message = !r}")
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
        message,
        reply=event.message,
    )
    logger.debug(f"Avatar URL: {await cx.pull(Avatar, cx.client)}")


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
    logger.debug(repr(event))


avilla.launch()
