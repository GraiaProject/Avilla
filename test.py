from inspect import cleandoc

from avilla.core.resource import LocalFileResource
from avilla.core.elements import Picture
from creart import create
from launart import Launart
from graia.amnesia.builtins.aiohttp import AiohttpClientService
from graia.broadcast import Broadcast

from avilla.core import Avilla, Context, MessageReceived
from avilla.elizabeth.connection.config import WebsocketClientConfig
from avilla.elizabeth.protocol import ElizabethProtocol

broadcast = create(Broadcast)
launart = Launart()
launart.add_service(AiohttpClientService())
avilla = Avilla(broadcast, launart, [ElizabethProtocol(WebsocketClientConfig("1779309090", "testafafv4fv34v34g3y45"))])


@broadcast.receiver(MessageReceived)
async def on_message_received(ctx: Context, event: MessageReceived):
    print(event, ctx.client, ctx.client.follows("group.member(208924405)"))
    if ctx.client.follows("group.member(208924405)"):
        await ctx.scene.send_message([Picture(LocalFileResource("./development/photo_2022-07-10_22-12-22.jpg"))])


avilla.launch_manager.launch_blocking(loop=broadcast.loop)
