from avilla.core import Avilla, Context, MessageReceived
from avilla.core.elements import Notice, Text
from avilla.satori.protocol import SatoriProtocol, SatoriConfig


config = SatoriConfig(
"localhost",
    5500,
    "9491ee65f2e5322d050021d4ceaca05d42c3ff2fc2a457fdffeb315619bf3f91"
)
avilla = Avilla(message_cache_size=0)
avilla.apply_protocols(SatoriProtocol().configure(config))


@avilla.listen(MessageReceived)
async def on_message_received(cx: Context, event: MessageReceived):
    print(cx.endpoint, cx.client)
    print(event.message.content)
    if cx.client.follows("::public.channel.member(3165388245)"):
        print(
            await cx.scene.send_message(
                [Notice(cx.client), Text("\nHello, Avilla!")]
            )
        )

avilla.launch()
