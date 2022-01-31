from typing import TYPE_CHECKING, Any, Optional, Type

from .utilles.selector import DepthSelector, Selector, SelectorKey

if TYPE_CHECKING:
    from avilla.core.resource import ResourceProvider


class entity(Selector):
    scope = "entity"

    if TYPE_CHECKING:
        mainline: SelectorKey["entity", "mainline"]
        account: SelectorKey["entity", str]
        friend: SelectorKey["entity", str]
        member: SelectorKey["entity", str]
        channel: SelectorKey["entity", str]  # 可以发消息的 channel, 类似 tg.

        group: SelectorKey["entity", Any]  # 于 mainline.group 不同，这里是拿来 “根据其他字段” 进行 multi config 的，因此这里可以随便填值。

    def get_mainline(self) -> "mainline":
        if "account" in self.path:
            return mainline._["$avilla:account"]
        return self.path["mainline"]

    def get_entity_type(self) -> str:
        return list(self.without_group().path.values())[-1]

    def without_group(self):
        return entity({k: v for k, v in self.path.items() if k != "group"})

    def __hash__(self) -> int:
        return hash(tuple(self.path.items()))

    @property
    def profile_name(self) -> str:
        return list(self.path.keys())[-1]


class mainline(DepthSelector):
    scope = "mainline"

    if TYPE_CHECKING:
        group: SelectorKey["mainline", str]
        channel: SelectorKey["mainline", str]
        guild: SelectorKey["mainline", str]

        _: SelectorKey["mainline", Any]

    def keypath(self) -> str:
        return super().keypath()


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
        dir: SelectorKey["resource", str]
        file: SelectorKey["resource", str]
        image: SelectorKey["resource", str]
        audio: SelectorKey["resource", str]
        video: SelectorKey["resource", str]
        sticker: SelectorKey["resource", str]
        animation: SelectorKey["resource", str]
        unknown: SelectorKey["resource", str]

        mainline: SelectorKey["resource", "mainline"]
        provider: SelectorKey["resource", "Type[ResourceProvider]"]

    def get_mainline(self) -> "mainline":
        return self.path["mainline"]

    @property
    def resource_type(self) -> str:
        return list(self.path.keys())[0]


class request(Selector):
    scope = "request"

    if TYPE_CHECKING:
        mainline: SelectorKey["request", "mainline"]
        via: SelectorKey["request", "entity"]
        _: SelectorKey["request", str]
        # 示例: request.mainline[mainline.group[123]]._[""]

    def get_mainline(self) -> "mainline":
        return self.path["mainline"]

    def get_via(self) -> Optional["entity"]:
        return self.path.get("via")
