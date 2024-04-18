import os

from avilla.core import Avilla, Context, MessageReceived
from avilla.core.elements import Text
from avilla.qqapi.element import Reference
from avilla.qqapi.protocol import QQAPIProtocol, QQAPIConfig, Intents


config = QQAPIConfig(
    os.getenv("QQGUILD_ID"),
    os.getenv("QQGUILD_TOKEN"),
    os.getenv("QQGUILD_SECRET"),
    is_sandbox=True,
    intent=Intents(guild_messages=True, at_messages=False, direct_message=True),
)

avilla = Avilla(message_cache_size=0)
avilla.apply_protocols(QQAPIProtocol().configure(config))


@avilla.listen(MessageReceived)
async def on_message_received(cx: Context, event: MessageReceived):
    # debug(cx.artifacts.maps)
    print(cx.client.channel)
    print(cx.client.user)
    print(event.message.content)
    print(
        await cx.scene.send_message(
            [
                Text("Hello, Avilla!"),
                # Embed(
                #     "Test Embed",
                #     "Hello, Avilla!",
                #     fields=["line1", "line2"],
                # )
            ],
            reply=event.message,
        )
    )
    print(await cx.scene.privilege())
    print(await cx.scene.nick())
    print(await cx.self.privilege())


avilla.launch()
