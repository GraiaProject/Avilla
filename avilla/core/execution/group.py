from . import Execution, Operation


class MemberRemove(Operation, Execution):
    pass


class MemberMute(Operation, Execution):
    duration: int

    def __init__(self, duration: int):
        super().__init__(duration=duration)


class MemberUnmute(Operation, Execution):
    pass


class GroupMute(Operation, Execution):
    pass


class GroupUnmute(Operation, Execution):
    pass


class MemberPromoteToAdministrator(Operation, Execution):
    pass


class MemberDemoteFromAdministrator(Operation, Execution):
    pass


class MemberNicknameSet(Operation, Execution):
    nickname: str

    def __init__(self, nickname: str):
        super().__init__(nickname=nickname)


class MemberNicknameClear(Operation, Execution):
    pass


class GroupNameSet(Operation, Execution):
    name: str

    def __init__(self, name: str):
        super().__init__(name=name)


class GroupLeave(Operation, Execution):
    pass


class MemberSpecialTitleSet(Operation, Execution):
    title: str

    def __init__(self, title: str):
        super().__init__(title=title)

    class Config:
        arbitrary_types_allowed = True
