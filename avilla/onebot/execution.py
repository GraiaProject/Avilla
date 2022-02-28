from typing import List, Union

from avilla.core.execution import MessageFetch, Result
from avilla.core.message import Message, MessageChain
from avilla.core.selectors import message as message_selector
from avilla.onebot.elements import Forward


class ForwardMessageFetch(MessageFetch, Result[List[Message]]):
    message: Union[message_selector, Message, MessageChain, Forward]

    def __init__(self, message: Union[message_selector, Message, MessageChain, Forward]):
        self.message = message
