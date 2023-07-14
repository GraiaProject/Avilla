from dataclasses import field, dataclass
from typing import List, Generic, TypeVar

from textual.widget import Widget
from textual.message import Message
from rich.console import RenderableType

from ..info import User, MessageEvent

MAX_LOG_RECORDS = 500
MAX_MSG_RECORDS = 500


T = TypeVar("T")


class StateChange(Message, Generic[T], bubble=False):
    def __init__(self, data: T) -> None:
        super().__init__()
        self.data = data


@dataclass
class Storage:
    current_user: User = field(default_factory=lambda: User(id="console"))

    log_history: List[RenderableType] = field(default_factory=list)
    log_watchers: List[Widget] = field(default_factory=list)

    chat_history: List[MessageEvent] = field(default_factory=list)
    chat_watchers: List[Widget] = field(default_factory=list)

    def set_user(self, user: User):
        self.current_user = user

    def write_log(self, *logs: RenderableType) -> None:
        self.log_history.extend(logs)
        if len(self.log_history) > MAX_LOG_RECORDS:
            self.log_history = self.log_history[-MAX_LOG_RECORDS:]
        self.emit_log_watcher(*logs)

    def add_log_watcher(self, watcher: Widget) -> None:
        self.log_watchers.append(watcher)

    def remove_log_watcher(self, watcher: Widget) -> None:
        self.log_watchers.remove(watcher)

    def emit_log_watcher(self, *logs: RenderableType) -> None:
        for watcher in self.log_watchers:
            watcher.post_message(StateChange(logs))

    def write_chat(self, *messages: "MessageEvent") -> None:
        self.chat_history.extend(messages)
        if len(self.chat_history) > MAX_MSG_RECORDS:
            self.chat_history = self.chat_history[-MAX_MSG_RECORDS:]
        self.emit_chat_watcher(*messages)

    def add_chat_watcher(self, watcher: Widget) -> None:
        self.chat_watchers.append(watcher)

    def remove_chat_watcher(self, watcher: Widget) -> None:
        self.chat_watchers.remove(watcher)

    def emit_chat_watcher(self, *messages: "MessageEvent") -> None:
        for watcher in self.chat_watchers:
            watcher.post_message(StateChange(messages))
