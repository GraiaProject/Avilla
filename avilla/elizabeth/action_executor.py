from __future__ import annotations

from avilla.core.action import MessageSend
from avilla.core.relationship import Relationship
from avilla.core.utilles.action_executor import ProtocolActionExecutor, action
from avilla.core.utilles.selector import Selector


class ElizabethFriendActionExecutor(ProtocolActionExecutor, pattern=Selector(match_rule="exist").friend(lambda _: True)):
    @action(MessageSend)
    def send_message(self, action: MessageSend, relationship: Relationship):
        # TODO
        ...