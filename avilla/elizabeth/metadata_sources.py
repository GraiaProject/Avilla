from typing import TYPE_CHECKING

from avilla.core.utilles.metadata_source import ProtocolMetadataSource, fetch

from ..core.context import ctx_relationship
from ..core.cell.cells import Count, Summary
from ..core.utilles.selector import Selector

if TYPE_CHECKING:
    from .protocol import ElizabethProtocol


class ElizabethGroupMetadataSource(ProtocolMetadataSource["ElizabethProtocol"], pattern="group"):
    @fetch(Summary)
    async def fetch_summary(self, target: Selector):
        data = await ctx_relationship.get().account.call(
            "groupConfig",
            {
                "__method__": "fetch",
                "target": target.pattern["group"],
            },
        )
        return Summary(
            target=target,
            source=self,
            content={
                "summary.name": data["name"],
                "summary.description": f"Group{(data['name'], target.pattern['group'])}",
            },
        )

    @fetch(Count)
    async def fetch_count(self, target: Selector):
        cnt = len(
            await ctx_relationship.get().account.call(
                "memberList",
                {
                    "__method__": "fetch",
                    "target": target.pattern["group"],
                },
            )
        )
        return Count(target=target, source=self, content={"count.current": cnt, "count.max": None})


class ElizabethMemberMetadataSource(ProtocolMetadataSource["ElizabethProtocol"], pattern="group.member"):
    @fetch(Summary)
    async def fetch_summary(self, target: Selector):
        name = (
            await ctx_relationship.get().account.call(
                "memberInfo",
                {
                    "__method__": "fetch",
                    "target": target.pattern["group"],
                    "memberId": target.pattern["member"],
                },
            )
        )["memberName"]
        sign = (
            await ctx_relationship.get().account.call(
                "memberProfile",
                {
                    "__method__": "get",
                    "target": target.pattern["group"],
                    "memberId": target.pattern["member"],
                },
            )
        )["sign"]

        return Summary(target=target, source=self, content={"summary.name": name, "summary.description": sign})
