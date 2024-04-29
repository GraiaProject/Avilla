import asyncio
import os

from graia.amnesia.message import MessageChain
from loguru import logger

from avilla.core import Avilla, Context, MessageReceived
from avilla.standard.core.message import (
    MessageEdit,
    MessageEdited,
    MessageRevoke,
    MessageRevoked,
    MessageSent,
)
from avilla.telegram.protocol import TelegramLongPollingConfig, TelegramProtocol

config = TelegramLongPollingConfig(os.environ["TELEGRAM_TOKEN"])
avilla = Avilla(message_cache_size=0)
avilla.apply_protocols(TelegramProtocol().configure(config))


@avilla.listen(MessageReceived)
async def on_message_received(ctx: Context, event: MessageReceived, message: MessageChain):
    logger.debug(f"MessageChain: {repr(message)}")
    sent = await ctx.scene.send_message(message, reply=event.message)
    await asyncio.sleep(1)
    if str(message) == "!edit":
        await ctx[MessageEdit.edit](sent, MessageChain("Edited!"))
    if str(message) == "!revoke":
        await ctx[MessageRevoke.revoke](sent)


@avilla.listen(MessageEdited)
async def on_message_edited(ctx: Context, event: MessageEdited):
    logger.debug(f"MessageEdited: {repr(event)}")


@avilla.listen(MessageRevoked)
async def on_message_revoked(ctx: Context, event: MessageRevoked):
    logger.debug(f"MessageRevoked: {repr(event)}")


@avilla.listen(MessageSent)
async def on_message_sent(ctx: Context, event: MessageSent):
    logger.debug(f"MessageSent: {repr(event)}")


avilla.launch()
