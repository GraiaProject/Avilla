from __future__ import annotations

from collections import deque
from typing import TYPE_CHECKING
from weakref import WeakValueDictionary

if TYPE_CHECKING:
    from avilla.core.message import Message
    from avilla.core.selector import Selector


class MessageCacheDeque:
    messages: deque[Message]
    _endpoint: WeakValueDictionary[Selector, Message]

    def __init__(self, cache_size: int) -> None:
        self.messages = deque(maxlen=cache_size)
        self._endpoint = WeakValueDictionary()

    def push(self, message: Message):
        self.messages.append(message)
        self._endpoint[message.to_selector()] = message

    def get(self, message_selector: Selector):
        return self._endpoint.get(message_selector)
