from __future__ import annotations

from avilla.core.context import Context
from avilla.core.event import RelationshipCreated
from avilla.core.selector import Selector
from avilla.core.ryanvk.descriptor.event import EventParse
from avilla.red.collector.connection import ConnectionCollector
from loguru import logger
from selectolax.parser import HTMLParser

# async function adaptGuildMemberAddedMessage(
#   session: Session,
#   data: Message,
# ): Promise<Session | undefined> {
#   const session2 = await adaptChatMessage(session, data)
#   session2.type = 'guild-member-added'
#
#   session2.operatorId =
#     data.elements[0]!.grayTipElement!.groupElement!.adminUin!
#   session2.author = {
#     userId: data.elements[0]!.grayTipElement!.groupElement!.memberUin!,
#     username: data.elements[0]!.grayTipElement!.groupElement!.memberNick!,
#     nickname: data.elements[0]!.grayTipElement!.groupElement!.memberNick!,
#   }
#   session2.userId = session2.author.userId
#
#   return session2
# }

class RedEventRelationshipPerform((m := ConnectionCollector())._):
    m.post_applying = True

    @EventParse.collect(m, "group::member::add")
    async def member_join(self, raw_event: dict):
        account = self.connection.account
        if account is None:
            logger.warning(f"Unknown account received message {raw_event}")
            return
        group = Selector().land(account.route["land"]).group(str(raw_event.get("peerUin", raw_event.get("peerUid"))))
        group_data = raw_event["elements"][0]["grayTipElement"]["groupElement"]
        member = group.member(str(group_data["memberUin"]))
        operator = group.member(str(group_data["adminUin"]))
        context = Context(
            account,
            member,
            group,
            group,
            group.member(account.route["account"]),
            mediums=[operator]
        )
        return RelationshipCreated(context)

    @EventParse.collect(m, "group::member::legacy::add::invited")
    async def member_join(self, raw_event: dict):
        account = self.connection.account
        if account is None:
            logger.warning(f"Unknown account received message {raw_event}")
            return
        group = Selector().land(account.route["land"]).group(str(raw_event.get("peerUin", raw_event.get("peerUid"))))
        group_data = raw_event["elements"][0]["grayTipElement"]["xmlElement"]
        root = HTMLParser(group_data["content"])
        operator = group.member(root.tags("qq")[0].attributes["jp"])
        member = group.member(root.tags("qq")[1].attributes["jp"])
        context = Context(
            account,
            member,
            group,
            group,
            group.member(account.route["account"]),
            mediums=[operator]
        )
        return RelationshipCreated(context)
