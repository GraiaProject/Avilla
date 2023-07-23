import os

from creart import create

from avilla.core import Avilla, Context, MessageReceived
from avilla.core.builtins.capability import CoreCapability
from avilla.core.elements import Text
from avilla.qqguild.tencent.connection.ws_client import Intents, QQGuildWsClientConfig, QQGuildWsClientNetworking
from avilla.qqguild.tencent.element import Reference
from avilla.qqguild.tencent.protocol import QQGuildProtocol
from avilla.standard.core.privilege import Privilege

# from graia.amnesia.builtins.aiohttp import AiohttpClientService
from graia.broadcast import Broadcast
from launart import Launart

#from avilla.console.protocol import ConsoleProtocol

#richuru1.install()

broadcast = create(Broadcast)
launart = Launart()
protocol = QQGuildProtocol()
service = protocol.service
config = QQGuildWsClientConfig(
    os.getenv("QQGUILD_ID"),
    os.getenv("QQGUILD_TOKEN"),
    os.getenv("QQGUILD_SECRET"),
    is_sandbox=True,
    intent=Intents(guild_messages=True, at_messages=False, direct_message=True),
)
conn = QQGuildWsClientNetworking(protocol, config)
service.connections.append(conn)

#console_protocol = ConsoleProtocol()
avilla = Avilla(broadcast, launart, [protocol], message_cache_size=0)

protocol.avilla = avilla



#debug(protocol.isolate.artifacts)
# exit()

# TODO(Networking): 自动注册 Account


@broadcast.receiver(MessageReceived)
async def on_message_received(cx: Context, event: MessageReceived):
    # debug(cx.artifacts.maps)
    print(cx.endpoint, cx.client)
    print(event.message.content)
    print(
        await cx.scene.send_message(
            [
                Reference(event.message.id),
                Text("Hello, Avilla!"),
                # Embed(
                #     "Test Embed",
                #     "Hello, Avilla!",
                #     fields=["line1", "line2"],
                # )
            ],
            reply=event.message
        )
    )
    print(
        await cx.scene.pull(Privilege)
    )
    print(
        await cx.client.pull(Privilege)
    )
    print(
        await cx[CoreCapability.pull](cx.self, Privilege)
    )


avilla.launch_manager.launch_blocking(loop=broadcast.loop)
