import os

from graia.amnesia.builtins.asgi import UvicornASGIService
from graia.amnesia.message import MessageChain
from loguru import logger
from yarl import URL

from avilla.core import Avilla, Context, MessageReceived
from avilla.standard.core.message import MessageSent
from avilla.telegram.protocol import TelegramProtocol, TelegramWebhookConfig

config = TelegramWebhookConfig(
    os.environ["TELEGRAM_TOKEN"],
    proxy=os.environ.get("HTTP_PROXY", None),
    webhook_url=URL(os.environ["TELEGRAM_WEBHOOK_URL"]),
    secret_token=os.environ.get("TELEGRAM_SECRET_TOKEN", None),
)
avilla = Avilla(message_cache_size=0)
avilla.apply_protocols(TelegramProtocol().configure(config))
avilla.launch_manager.add_component(UvicornASGIService("127.0.0.1", 9090))


@avilla.listen(MessageReceived)
async def on_message_received(ctx: Context, event: MessageReceived, msg: MessageChain):
    logger.info(f"Received: {repr(event)}")
    logger.info(f"Message: {msg}")


@avilla.listen(MessageSent)
async def on_message_sent(event: MessageSent):
    logger.info(f"Sent: {repr(event)}")


avilla.launch()
