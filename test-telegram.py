import os
from pathlib import Path

from graia.amnesia.message import MessageChain

from avilla.core import Avilla, Context, MessageReceived, Picture, Text
from avilla.telegram.bot.bot import TelegramBot
from avilla.telegram.protocol import TelegramProtocol, TelegramBotConfig

protocol = TelegramProtocol()
service = protocol.service
config = TelegramBotConfig(os.environ["TELEGRAM_TOKEN"])
bot = TelegramBot(protocol, config)
service.instances.append(bot)

avilla = Avilla(message_cache_size=0)
avilla.apply_protocols(protocol)

protocol.avilla = avilla


@avilla.listen(MessageReceived)
async def on_message_received(cx: Context, event: MessageReceived):
    print(repr(event))
    await cx.scene.send_message(MessageChain([Text("Hello, Avilla!"), Picture(Path("test.png"))]))


avilla.launch()
