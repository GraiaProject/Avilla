from creart import create
from graia.amnesia.builtins.aiohttp import AiohttpClientService
from graia.broadcast import Broadcast

from avilla.core import Avilla, Context, MessageReceived
from avilla.elizabeth.connection.config import WebsocketClientConfig
from avilla.elizabeth.protocol import ElizabethProtocol

broadcast = create(Broadcast)
avilla = Avilla(
    broadcast, [ElizabethProtocol(WebsocketClientConfig("bot-account", "mah-verify-code"))], [AiohttpClientService()]
)


@broadcast.receiver(MessageReceived)
async def on_message_received(ctx: Context, event: MessageReceived):
    if ctx.client.follows("group.member(<master-account>)"):
        await ctx.scene.send_message("Hello, Avilla!")


avilla.launch_manager.launch_blocking(loop=broadcast.loop)
