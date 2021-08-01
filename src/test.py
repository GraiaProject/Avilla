from pathlib import Path
import traceback
import aiohttp
from graia.broadcast import Broadcast
from yarl import URL
from avilla import Avilla, context
import avilla.entity
import avilla.exceptions
import avilla.group
from avilla.onebot.config import OnebotConfig, WebsocketCommunication
import avilla.profile
import avilla.protocol
from avilla.provider import FileProvider, HttpGetProvider
import avilla.relationship
import avilla.role
import avilla.builtins
import avilla.builtins.elements
import avilla.builtins.profile
import avilla.event
from avilla.event.message import MessageEvent
from avilla.relationship import Relationship
import avilla.event.notice
import avilla.event.request
import avilla.event.service
import avilla.execution
import avilla.execution.fetch
import avilla.execution.group
import avilla.execution.message
import avilla.execution.request
import avilla.message.chain
import avilla.message.element
import avilla.onebot.protocol
from avilla.network.clients.aiohttp import AiohttpHttpClient, AiohttpWebsocketClient
from avilla.onebot.event_tree import EVENT_PARSING_TREE, gen_parsing_key
print(EVENT_PARSING_TREE)

import asyncio

loop = asyncio.get_event_loop()

broadcast = Broadcast(loop=loop)
session = aiohttp.ClientSession(loop=loop)
avilla_app: Avilla[avilla.onebot.protocol.OnebotProtocol, OnebotConfig] = avilla.Avilla(broadcast, avilla.onebot.protocol.OnebotProtocol, {
    "ws": AiohttpWebsocketClient(session),
}, {
    avilla.onebot.protocol.OnebotProtocol: OnebotConfig(
        access_token='avilla-test',
        bot_id=208924405,
        communications={
            "ws": WebsocketCommunication(api_root=URL("ws://127.0.0.1:6700/"))
        }
    )
})

@broadcast.receiver(MessageEvent)
async def on_message(event: MessageEvent, rs: Relationship[avilla.builtins.profile.MemberProfile, avilla.builtins.profile.GroupProfile, OnebotConfig]):
    try:
        #print("娇小的少女迈出了她柔弱却意义非凡的第一步.")
        #print(event);
        print(rs.entity_or_group)

        #print(isinstance(rs.entity_or_group.profile, avilla.builtins.profile.MemberProfile), rs.entity_or_group.id == "1846913566")
        if isinstance(rs.entity_or_group.profile, avilla.builtins.profile.MemberProfile) and rs.entity_or_group.id == "1846913566":
            await rs.exec(avilla.execution.message.MessageSend(
                avilla.message.chain.MessageChain.create([
                    avilla.builtins.elements.Notice(rs.entity_or_group.id), avilla.builtins.elements.PlainText("发图测试"),
                    avilla.builtins.elements.Image(FileProvider(Path("D:/pixiv/56340791_p0.jpg")))
                ])
            ))
    except:
        traceback.print_exc()

TEST_DATA = {'anonymous': None, 'font': 0, 'group_id': 372286357, 'message': [{'data': {'text': '测试111'}, 'type': 'text'}], 'message_id': -76565625, 'message_seq': 2976667, 'message_type': 'group', 'post_type': 'message', 'raw_message': '测试111', 'self_id': 208924405, 'sender': {'age': 0, 'area': '', 'card': 'GreyElaina', 'level': '', 'nickname': 'Elaina', 'role': 'member', 'sex': 'unknown', 'title': '', 'user_id': 1846913566}, 'sub_type': 'normal',
'time': 1627798990, 'user_id': 1846913566}

async def m():
    event_parser = EVENT_PARSING_TREE.get(gen_parsing_key(TEST_DATA))
    if event_parser:
        event = await event_parser(avilla_app.protocol, TEST_DATA)
        with (
            context.ctx_avilla.use(avilla_app),
            context.ctx_event.use(event),
            context.ctx_protocol.use(avilla_app.protocol)
        ):
            broadcast.postEvent(event)
    else:
        print('cannot parse event:', gen_parsing_key(TEST_DATA), TEST_DATA)
    
    await asyncio.sleep(1)

async def main():
    await avilla_app.launch()

    while 1:
        await asyncio.sleep(1)

import pprint
#pprint.pprint(avilla.onebot.protocol.OnebotProtocol._ensure_execution.overrides)
loop.run_until_complete(main())
#loop.run_until_complete(m())