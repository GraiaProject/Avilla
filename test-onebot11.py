from avilla.core import Avilla, Context, MessageReceived
from avilla.onebot.v11.protocol import OneBot11Protocol, OneBot11ReverseConfig

from graia.amnesia.builtins.asgi import UvicornASGIService

avilla = Avilla()


config = OneBot11ReverseConfig(endpoint="ws", access_token="dfawdfafergergeaar")
avilla.apply_protocols(OneBot11Protocol().configure(config))
avilla.launch_manager.add_component(UvicornASGIService("127.0.0.1", 9555))


@avilla.listen(MessageReceived)
async def on_message_received(ctx: Context, event: MessageReceived):
    await ctx.scene.send_message("Hello, Avilla!")

avilla.launch()
