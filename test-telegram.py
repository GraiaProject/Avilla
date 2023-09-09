import os

from graia.amnesia.message import MessageChain

from avilla.core import Avilla, Context, MessageReceived, Text
from avilla.telegram.protocol import TelegramProtocol, TelegramBotConfig

config = TelegramBotConfig(os.environ["TELEGRAM_TOKEN"])
avilla = Avilla(message_cache_size=0)
avilla.apply_protocols(TelegramProtocol().configure(config))


@avilla.listen(MessageReceived)
async def on_message_received(cx: Context, event: MessageReceived):
    print(repr(event))
    await cx.scene.send_message(MessageChain([Text("Hello, Avilla!")]))


avilla.launch()
