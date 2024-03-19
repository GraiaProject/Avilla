from avilla.core import Avilla, Context, MessageReceived
from avilla.console.protocol import ConsoleProtocol
from avilla.console.element import Markdown
from avilla.core.elements import Face

avilla = Avilla()
avilla.apply_protocols(ConsoleProtocol())


from flywheel.globals import GLOBAL_INSTANCE_CONTEXT

@avilla.listen(MessageReceived)
async def on_message_received(ctx: Context, event: MessageReceived):
    msg = str(event.message.content)
    if msg == "/help":
        await ctx.scene.send_message(
            [Markdown("""\
## 菜单
- /help
- /echo
- /md
- /emoji
"""
            )])
    elif msg == "/md":
        await ctx.scene.send_message(
            [Markdown("""\
# Avilla-Console

`avilla` 的 `Console` 适配，使用 `Textual`

参考: [`nonebot-adapter-console`](https://github.com/nonebot/adapter-console)

## 样例

```python
from avilla.core import Avilla, Context, MessageReceived
from avilla.console.protocol import ConsoleProtocol

avilla = Avilla()
avilla.apply_protocols(ConsoleProtocol())


@broadcast.receiver(MessageReceived)
async def on_message_received(ctx: Context):
    await ctx.scene.send_message("Hello, Avilla!")

avilla.launch()
```
"""
            )]
        )
    elif msg == "/emoji":
        await ctx.scene.send_message([Face("art"), " | this is apple -> ", Face("apple")])
    else:
        await ctx.scene.send_message("Hello, Avilla!")

avilla.launch()
