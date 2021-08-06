from avilla.builtins.profile import FriendProfile, GroupProfile, MemberProfile
from avilla.relationship import Relationship


def is_member(rs: Relationship):
    return isinstance(rs.ctx.profile, MemberProfile)


def is_group(rs: Relationship):
    return isinstance(rs.ctx.profile, GroupProfile)


def is_friend(rs: Relationship):
    return isinstance(rs.ctx.profile, FriendProfile)
