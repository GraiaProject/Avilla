import asyncio
from inspect import cleandoc

from creart import create
from graia.amnesia.builtins.aiohttp import AiohttpClientService
from graia.broadcast import Broadcast
from launart import Launart

from avilla.core import Avilla, Context, MessageReceived
from avilla.core.elements import Picture
from avilla.core.resource import LocalFileResource
from avilla.elizabeth.connection.config import WebsocketClientConfig
from avilla.elizabeth.protocol import ElizabethProtocol
from avilla.spec.core.message.skeleton import MessageRevoke

# import richuru
# richuru.install()

broadcast = create(Broadcast)
launart = Launart()
launart.add_service(AiohttpClientService())
avilla = Avilla(
    broadcast, launart, [ElizabethProtocol(WebsocketClientConfig("208924405", "test"))], message_cache_size=0
)


@broadcast.receiver(MessageReceived)
async def on_message_received(cx: Context, event: MessageReceived):
    if cx.client.follows("group.member(1846913566)"):
        await cx.scene.send_message("Hello, Avilla!")


async def log():
    while True:
        await asyncio.sleep(5)
        print("i'm alive!")
        print(await avilla.get_account("208924405").call("groupList", {"__method__": "fetch"}))


t = broadcast.loop.create_task(log())

avilla.launch_manager.launch_blocking(loop=broadcast.loop)
