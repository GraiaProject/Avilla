import os

from graia.amnesia.message import MessageChain
from loguru import logger

from avilla.core import Avilla, Context, MessageReceived
from avilla.standard.core.message import MessageSent
from avilla.telegram.protocol import TelegramLongPollingConfig, TelegramProtocol

config = TelegramLongPollingConfig(os.environ["TELEGRAM_TOKEN"], proxy=os.environ.get("HTTP_PROXY", None))
avilla = Avilla(message_cache_size=0)
avilla.apply_protocols(TelegramProtocol().configure(config))


@avilla.listen(MessageReceived)
async def on_message_received(ctx: Context, event: MessageReceived, msg: MessageChain):
    logger.info(f"Received: {repr(event)}")
    logger.info(f"Message: {msg}")


@avilla.listen(MessageSent)
async def on_message_sent(event: MessageSent):
    logger.info(f"Sent: {repr(event)}")


avilla.launch()
