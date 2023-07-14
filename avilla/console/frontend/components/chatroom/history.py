from datetime import datetime, timedelta
from typing import TYPE_CHECKING, Tuple, Iterable, Optional, cast

from textual.widget import Widget

from .message import Timer, Message

if TYPE_CHECKING:
    from ...app import Frontend
    from ...info import MessageEvent
    from ...storage import Storage, StateChange


class ChatHistory(Widget):
    DEFAULT_CSS = """
    ChatHistory {
        layout: vertical;
        height: 100%;
        overflow: hidden scroll;
        scrollbar-size-vertical: 1;
    }
    """

    def __init__(self):
        super().__init__()
        self.last_msg: Optional["MessageEvent"] = None
        self.last_time: Optional[datetime] = None

    @property
    def storage(self) -> "Storage":
        return cast("Frontend", self.app).storage

    async def on_mount(self):
        await self.on_new_message(self.storage.chat_history)
        self.storage.add_chat_watcher(self)

    def on_unmount(self):
        self.storage.remove_chat_watcher(self)

    async def action_new_message(self, message: "MessageEvent"):
        if (
            not self.last_time
            or message.time - self.last_time > timedelta(minutes=5)
            or (
                self.last_msg
                and message.time - self.last_msg.time > timedelta(minutes=1)
            )
        ):
            self.mount(Timer(message.time))  # noqa
            self.last_time = message.time
        await self.mount(Message(message))
        self.last_msg = message

        self.scroll_end()

    async def on_state_change(self, event: "StateChange[Tuple[MessageEvent, ...]]"):
        await self.on_new_message(event.data)

    async def on_new_message(self, messages: Iterable["MessageEvent"]):
        for message in messages:
            await self.action_new_message(message)

    def action_clear_history(self):
        self.last_msg = None
        self.last_time = None
        for msg in self.walk_children():
            cast(Widget, msg).remove()
        self.storage.chat_history.clear()
