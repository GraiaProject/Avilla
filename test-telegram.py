import os
from pathlib import Path

from graia.amnesia.message import MessageChain

from avilla.core import Avilla, Context, MessageReceived, Picture, Text, Video
from avilla.standard.core.message import MessageSent
from avilla.standard.telegram.event import ForumTopicClosed, ForumTopicCreated
from avilla.telegram.protocol import TelegramBotConfig, TelegramProtocol

config = TelegramBotConfig(os.environ["TELEGRAM_TOKEN"], reformat=True)
avilla = Avilla(message_cache_size=0)
avilla.apply_protocols(TelegramProtocol().configure(config))


@avilla.listen(MessageReceived)
async def on_message_received(cx: Context, event: MessageReceived):
    print(repr(event))
    # await cx.scene.send_message(
    #     MessageChain(
    #         [
    #             Text("Hello, Avilla!"),
    #             Picture(Path("test.jpg")),
    #             Video(Path("test.mp4")),
    #         ]
    #     )
    # )


@avilla.listen(ForumTopicCreated)
async def forum_topic_created(cx: Context):
    await cx.scene.send_message(MessageChain([Text("Event: ForumTopicCreated")]))


@avilla.listen(ForumTopicClosed)
async def forum_topic_closed(cx: Context):
    await cx.scene.send_message(MessageChain([Text("Event: ForumTopicClosed")]))


@avilla.listen(MessageSent)
async def on_message_sent(event: MessageSent):
    print(repr(event))


avilla.launch()
