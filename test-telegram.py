import os

from avilla.core import Avilla, Context, MessageReceived
from avilla.telegram.bot import TelegramBotConfig, TelegramBot
from avilla.telegram.protocol import TelegramProtocol

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

avilla.launch()
