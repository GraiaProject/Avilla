import os
from yarl import URL

from avilla.core import Avilla, Context, MessageReceived

from avilla.red.net.ws_client import RedWsClientNetworking, RedWsClientConfig
from avilla.red.protocol import RedProtocol

protocol = RedProtocol()
service = protocol.service
config = RedWsClientConfig(
    URL("ws://localhost:16530"),
    os.getenv("QQNT_TOKEN")
)
conn = RedWsClientNetworking(protocol, config)
service.connections.append(conn)

avilla = Avilla( message_cache_size=0)
avilla.apply_protocols(protocol)

protocol.avilla = avilla


@avilla.listen(MessageReceived)
async def on_message_received(cx: Context, event: MessageReceived):
    # debug(cx.artifacts.maps)
    print(cx.endpoint, cx.client)
    print(event.message.content)
    if cx.scene.follows("::group(941310484)"):
        await cx.scene.send_message("Hello, Avilla!")

    if str(event.message.content).startswith("echo "):
        await cx.scene.send_message(
            event.message.content.removeprefix("echo ")
        )


avilla.launch(loop=avilla.broadcast.loop)
