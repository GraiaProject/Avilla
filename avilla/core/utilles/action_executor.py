from __future__ import annotations

import inspect
import warnings
from typing import (
    TYPE_CHECKING,
    Any,
    Callable,
    ClassVar,
    Coroutine,
    Generic,
    TypeVar,
    cast,
)

from typing_extensions import Self

from avilla.core.action import Action, StandardActionImpl
from avilla.core.relationship import Relationship
from avilla.core.utilles.selector import Selector

if TYPE_CHECKING:
    from avilla.core.protocol import BaseProtocol

NonstandardActionImplement = Callable[["ActionExecutor", Action, Relationship], Coroutine[None, None, Any]]


def action(*action_types: type[Action]):
    def decorator(implement: Any):
        cast(Any, implement).__supported_actions__ = action_types
        return implement

    return decorator


class ActionExecutor:
    implements: ClassVar[
        dict[
            type[Action],
            type[StandardActionImpl] | Callable[[Self, Action, Relationship], Coroutine[None, None, Any]],
        ]
    ] = {}
    pattern: ClassVar[Selector | None] = None
    # 给外部调用 match
    # 如果是 None, 表示不对其做约束...并且适用于我们不知道 target 到底是什么的情况.
    # 这适用于与平台数据无关的, 比如说我们可以有个 GetVersion(当然实际中我建议 Version) 的 Action, 他不需要 target.

    def __init_subclass__(cls, pattern: Selector | None = None):
        super().__init_subclass__()
        cls.implements = {}
        for mro in reversed(inspect.getmro(cls)):
            if issubclass(mro, ActionExecutor):
                cls.implements.update(mro.implements)
        members = inspect.getmembers(cls)
        for _, value in members:
            if inspect.isclass(value) and issubclass(value, StandardActionImpl):
                cls.implements.update({action_type: value for action_type in value.actions})
            else:
                actions: list[type[Action]] = getattr(value, "__supported_actions__", [])
                if actions:
                    cls.implements.update({action_type: value for action_type in actions})
        if pattern is not None:
            cls.pattern = pattern

    def get_implement(self, action: Action):
        handler = self.implements.get(type(action))
        if handler is None:
            raise NotImplementedError(f"Action {type(action)} is not supported.")
        return handler


_P = TypeVar("_P", bound="BaseProtocol")


class ProtocolActionExecutor(ActionExecutor, Generic[_P]):
    protocol: _P

    def __init__(self, protocol: _P) -> None:
        self.protocol = protocol
