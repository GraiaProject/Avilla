import os
from avilla.core import Avilla, Context, MessageReceived
from avilla.red.protocol import RedProtocol, RedConfig


config = RedConfig(os.getenv("QQNT_TOKEN"))
avilla = Avilla( message_cache_size=0)
avilla.apply_protocols(RedProtocol().configure(config))


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


avilla.launch()
