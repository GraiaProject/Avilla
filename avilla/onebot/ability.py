from avilla.core.builtins.elements import Image, Notice, NoticeAll, Quote, Text, Video, Voice
from avilla.core.builtins.profile import (
    FriendProfile,
    GroupProfile,
    MemberProfile,
    SelfProfile,
    StrangerProfile,
)
from avilla.core.event.notice import (
    FriendAdd,
    FriendRevoke,
    GroupFileUploadNotice,
    GroupRevoke,
    MemberDemotedFromAdministrator,
    MemberJoinedByApprove,
    MemberJoinedByInvite,
    MemberLeave,
    MemberMuted,
    MemberPromotedToAdministrator,
    MemberRemoved,
    MemberUnmuted,
)
from avilla.core.event.request import FriendAddRequest, GroupJoinRequest
from avilla.core.event.service import NetworkConnected, ServiceOffline, ServiceOnline
from avilla.onebot.elements import (
    Anonymous,
    Dice,
    Face,
    FriendRecommend,
    GroupRecommend,
    JsonMessage,
    Location,
    MergedForward,
    MergedForwardCustomNode,
    Poke,
    Rps,
    Shake,
    Share,
    XmlMessage,
)
from avilla.onebot.event import HeartbeatReceived, NudgeEvent

ABILITIES = {
    i.get_ability_id()
    for i in [
        FriendAdd,
        FriendRevoke,
        GroupFileUploadNotice,
        GroupRevoke,
        MemberDemotedFromAdministrator,
        MemberJoinedByApprove,
        MemberJoinedByInvite,
        MemberLeave,
        MemberMuted,
        MemberPromotedToAdministrator,
        MemberRemoved,
        MemberUnmuted,
        FriendAddRequest,
        GroupJoinRequest,
        NetworkConnected,
        ServiceOffline,
        ServiceOnline,
        HeartbeatReceived,
        NudgeEvent,
        Anonymous,
        Dice,
        Face,
        FriendRecommend,
        GroupRecommend,
        JsonMessage,
        Location,
        MergedForward,
        MergedForwardCustomNode,
        Poke,
        Rps,
        Shake,
        Share,
        XmlMessage,
        Image,
        Notice,
        NoticeAll,
        Text,
        Quote,
        Video,
        Voice,
        MemberProfile,
        GroupProfile,
        FriendProfile,
        StrangerProfile,
        SelfProfile,
    ]
}
