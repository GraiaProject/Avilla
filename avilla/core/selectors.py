from typing import TYPE_CHECKING

from .utilles.selector import Selector, SelectorKey


class entity(Selector):
    scope = "entity"


class mainline(Selector):
    scope = "mainline"

    if TYPE_CHECKING:
        group: SelectorKey["mainline", str]
        channel: SelectorKey["mainline", str]
        guild: SelectorKey["mainline", str]


class self(Selector):
    scope = "self"
