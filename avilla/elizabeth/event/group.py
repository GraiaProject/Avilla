from __future__ import annotations

from typing import TYPE_CHECKING, Any

from avilla.core.context import Context
from avilla.core.event import MetadataModified, Op, Update
from avilla.core.selector import Selector
from avilla.core.trait.context import EventParserRecorder
from avilla.spec.core.privilege.metadata import MuteInfo
from avilla.spec.core.privilege.skeleton import MuteAllTrait
from avilla.spec.core.profile.metadata import Nick
from avilla.spec.core.profile.skeleton import NickTrait

if TYPE_CHECKING:
    from ..account import ElizabethAccount
    from ..protocol import ElizabethProtocol


event = EventParserRecorder["ElizabethProtocol", "ElizabethAccount"]


@event("GroupNameChangeEvent")
async def group_name_changed(protocol: ElizabethProtocol, account: ElizabethAccount, raw: dict[str, Any]):
    group = Selector().land(protocol.land).group(str(raw["group"]["id"]))
    selft = group.member(account.id)
    if raw["operator"] is None:
        operator = selft
    else:
        operator = group.member(str(raw["operator"]["id"]))
    context = Context(account, operator, group, group, selft)
    return (
        MetadataModified(
            context=context,
            endpoint=group,
            modifies=[
                Op(
                    NickTrait.set_name,
                    {Nick.of(group): [Update(Nick.inh(lambda x: x.name), raw["current"], raw["origin"])]},
                )
            ],
            client=operator,
        ),
        context,
    )


@event("GroupMuteAllEvent")
async def group_muteall(protocol: ElizabethProtocol, account: ElizabethAccount, raw: dict[str, Any]):
    group = Selector().land(protocol.land).group(str(raw["group"]["id"]))
    selft = group.member(account.id)
    if raw["operator"] is None:
        operator = selft
    else:
        operator = group.member(str(raw["operator"]["id"]))
    context = Context(account, operator, group, group, selft)
    return (
        MetadataModified(
            context=context,
            endpoint=group,
            modifies=[
                Op(
                    MuteAllTrait.mute_all,
                    {MuteInfo.of(group): [Update(MuteInfo.inh(lambda x: x.muted), raw["current"], raw["origin"])]},
                )
            ],
            client=operator,
        ),
        context,
    )
