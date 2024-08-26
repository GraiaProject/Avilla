import os

from loguru import logger
from yarl import URL

from avilla.core import Avilla, Context, MessageReceived, Selector
from avilla.onebot.v11.protocol import OneBot11ForwardConfig, OneBot11Protocol
from avilla.standard.core.profile import Nick, Summary

avilla = Avilla()


# config = OneBot11ReverseConfig(endpoint="ws", access_token="dfawdfafergergeaar")
config = OneBot11ForwardConfig(
    endpoint=URL(os.environ["ONEBOT11_ENDPOINT"]), access_token=os.environ["ONEBOT11_ACCESS_TOKEN"]
)
avilla.apply_protocols(OneBot11Protocol().configure(config))
# avilla.launch_manager.add_component(UvicornASGIService("127.0.0.1", 9555))


@avilla.listen(MessageReceived)
async def on_message_received(ctx: Context):
    nick: Nick = await ctx.pull(Nick, ctx.client)
    summary: Summary = await ctx.pull(Summary, ctx.scene)
    stranger_nick: Nick = await ctx.pull(Nick, Selector().land(ctx.land).stranger("2854196310"))  # Q群管家
    logger.success(f"{nick = }")
    logger.success(f"{summary = }")
    logger.success(f"{stranger_nick = }")


avilla.launch()
