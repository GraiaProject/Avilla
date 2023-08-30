from avilla.core import Avilla, Context, MessageReceived
from avilla.core.elements import Notice, Text
from avilla.elizabeth.protocol import ElizabethProtocol, ElizabethConfig
from avilla.standard.core.privilege import Privilege


config = ElizabethConfig(
3542928737,
    "localhost",
    9080,
    "INITKEYWylsVdbr",
)
avilla = Avilla(message_cache_size=0)
avilla.apply_protocols(ElizabethProtocol().configure(config))


@avilla.listen(MessageReceived)
async def on_message_received(cx: Context, event: MessageReceived):
    # debug(cx.artifacts.maps)
    print(cx.endpoint, cx.client)
    print(event.message.content)
    if cx.client.follows("::group.member(3165388245)"):
        print(
            await cx.scene.send_message(
                [
                    Notice(cx.client),
                    Text("\nHello, Avilla!"),
                    # Picture("C:\\Users\\TR\\Pictures\\QQ图片20210814001401.jpg")
                    # Embed(
                    #     "Test Embed",
                    #     "Hello, Avilla!",
                    #     fields=["line1", "line2"],
                    # )
                ],
            )
        )
        # await asyncio.sleep(1)
        # msg = await cx.scene.send_message("test")
        # await asyncio.sleep(3)
        # await cx[MessageRevoke.revoke](msg)
        # print(await cx.account.connection.call("fetch", "friendList", {}))
        # async for i in cx.query("land.group(592387986).announcement"):
        #     print(await cx.pull(Announcement, i))
        # await cx[NickCapability.set_nickname](cx.scene.into("~.member(2582049752)"), "Abylance")
        # await cx[SummaryCapability.set_name](cx.scene, Summary, "测试群")
        print(await cx.pull(Privilege, cx.scene))
        print(await cx.pull(Privilege, cx.client))
        print(await cx.pull(Privilege, cx.self))

avilla.launch()
