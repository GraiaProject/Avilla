import re
from datetime import datetime

from graia.saya import Channel
from graia.saya.builtins.broadcast.schema import ListenerSchema

from avilla.core import Context, MessageChain, MessageReceived

channel = Channel.current()

pat = re.compile("(早安|(早上|中午|下午|晚上)好)")


@channel.use(ListenerSchema([MessageReceived]))
async def hello(cx: Context, event: MessageReceived, message: MessageChain):
    msg = str(message)
    now = datetime.now()
    if pat.search(msg):
        if 6 <= now.hour < 11:
            reply = "ο(=•ω＜=)ρ⌒☆\n早上好~"
        elif 11 <= now.hour < 13:
            reply = "(o゜▽゜)o☆\n中午好~"
        elif 13 <= now.hour < 18:
            reply = "（＾∀＾●）ﾉｼ\n下午好~"
        elif 18 <= now.hour < 24:
            reply = "ヾ(≧ ▽ ≦)ゝ\n晚上好~"
        else:
            reply = "≧ ﹏ ≦\n时候不早了，睡觉吧"
        await cx.scene.send_message(reply, reply=event.message)

    if msg.startswith("晚安") or msg.endswith("晚安"):
        if 0 <= now.hour < 6:
            reply = "时候不早了，睡觉吧~(￣o￣) . z Z"
        elif 20 < now.hour < 24:
            reply = "快睡觉~(￣▽￣)"
        else:
            reply = "喂，现在可不是休息的时候╰（‵□′）╯"
        await cx.scene.send_message(reply, reply=event.message)
