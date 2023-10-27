from graia.saya import Channel
from graia.saya.builtins.broadcast.schema import ListenerSchema

from avilla.core import Context, MessageChain, MessageReceived

channel = Channel.current()

DEFAULT_ECHO = "你发出一声不成言语的啼鸣，而只闻得回声四荡。"


@channel.use(ListenerSchema([MessageReceived]))
async def hello(cx: Context, message: MessageChain):
    if message.startswith("/echo"):
        await cx.scene.send_message(message.removeprefix("/echo", copy=True).removeprefix(" ") or DEFAULT_ECHO)
