from typing import TYPE_CHECKING, Optional

from .utilles.selector import Selector, SelectorKey


class entity(Selector):
    scope = "entity"

    if TYPE_CHECKING:
        account: SelectorKey["entity", str]
        mainline: SelectorKey["entity", "mainline"]
        member: SelectorKey["entity", str]
        friend: SelectorKey["entity", str]
        channel: SelectorKey["entity", str]  # 可以发消息的 channel, 类似 tg.

    def get_mainline(self) -> "mainline":
        return self.path["mainline"]

    @property
    def profile_name(self) -> str:
        return list(self.path.keys())[-1]


class mainline(Selector):
    scope = "mainline"

    if TYPE_CHECKING:
        group: SelectorKey["mainline", str]
        channel: SelectorKey["mainline", str]
        guild: SelectorKey["mainline", str]


class self(Selector):
    scope = "self"


class message(Selector):
    scope = "message"

    if TYPE_CHECKING:
        mainline: SelectorKey["message", "mainline"]
        _: SelectorKey["message", str]

    def get_mainline(self) -> "mainline":
        return self.path["mainline"]


class resource(Selector):
    scope = "resource"

    if TYPE_CHECKING:
        file: SelectorKey["resource", str]
        image: SelectorKey["resource", str]
        audio: SelectorKey["resource", str]
        video: SelectorKey["resource", str]
        sticker: SelectorKey["resource", str]
        animation: SelectorKey["resource", str]
        unknown: SelectorKey["resource", str]

        mainline: SelectorKey["resource", "mainline"]

    def get_mainline(self) -> "mainline":
        return self.path["mainline"]


class request(Selector):
    scope = "request"

    if TYPE_CHECKING:
        mainline: SelectorKey["request", "mainline"]
        via: SelectorKey["request", "entity"]
        _: SelectorKey["request", str]

    def get_mainline(self) -> "mainline":
        return self.path["mainline"]

    def get_via(self) -> Optional["entity"]:
        return self.path.get("via")
