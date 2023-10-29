from __future__ import annotations

from typing import TYPE_CHECKING

from graia.amnesia.message import Element, MessageChain

from avilla.core.event import AvillaEvent
from avilla.core.ryanvk.collector.application import ApplicationCollector
from graia.ryanvk import Fn, PredicateOverload, TypeOverload

if TYPE_CHECKING:
    pass


class NoneBridgeCapability((m := ApplicationCollector())._):
    # @Fn.complex({TypeOverload()})
    # TODO: ContextOverload, TargetOverload?
    #       我在设想一种可能性……一种更自由的组成办法，但现在还是先把 ContextOverload 搞出来吧。
    #       ContextOverload(provider=lambda args: args['event'].context)
    #       本质是对 TargetOverload 的扩展，应该有更好的方法。
    #       "Express"。不幸的，我现在不怎么喜欢 ContextVar。
    #       外部提供信息给 executor/evaluater, 然后再丢回给 behavior? 似乎是很好的办法。
    #       可选信息用 `Session/Context` 之类的。然后最好是直接分派给其他 Overload。
    #       麻烦的，就是我希望可以重置一下 Overload，现在的参数真是 raw & low-level & native，不合适。
    #
    ...
