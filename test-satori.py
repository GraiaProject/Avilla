from avilla.core import Avilla, Context, MessageReceived, MessageSent
from avilla.core.elements import Notice, Text
from avilla.satori.protocol import SatoriProtocol, SatoriConfig


config = SatoriConfig(
    "localhost",
    12345,
    path="foo"
)
avilla = Avilla(message_cache_size=0)
avilla.apply_protocols(SatoriProtocol().configure(config))


@avilla.listen(MessageReceived)
async def on_message_received(cx: Context, event: MessageReceived):
    print(cx.endpoint, cx.client)
    print(event.message.content)
    if event.message.content.startswith("test"):
        print(
            await cx.scene.send_message(
                [Text("Hello, Avilla!\nPowered by Satori!")]
            )
        )

avilla.launch()
