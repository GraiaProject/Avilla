from inspect import cleandoc

from graia.saya import Channel
from graia.saya.builtins.broadcast.schema import ListenerSchema

from avilla.core import Context, MessageChain, MessageReceived

channel = Channel.current()


@channel.use(ListenerSchema([MessageReceived]))
async def hello(cx: Context, message: MessageChain):
    if message.startswith("/hello"):
        await cx.scene.send_message(
            cleandoc(
                """
            Hello there! 👋
            如果你能收到这条消息，则 hello 插件已经部署并可用，你可以尝试在其他地方，\
            例如群聊，子频道，终端或是好友私信中尝试以同样的方法触发这条消息。

            我们欢迎你使用 Avilla 进行进一步的开发，你可以尝试复制该插件的模块，\
            并以此为基础尝试更多 Avilla 的用法，具体的详情还请参考相关文档。

            “探索与创造应是人们所追求不懈的。”
        """
            )
        )
