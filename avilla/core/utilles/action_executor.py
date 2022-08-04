from __future__ import annotations

import inspect
from typing import TYPE_CHECKING, Any, Callable, ClassVar, Generic, TypeVar, Union

from typing_extensions import Self

from avilla.core.action import Action as NonStandardAction, StandardActionImpl as StandardAction
from avilla.core.relationship import Relationship, RelationshipExecutor
from avilla.core.utilles.selector import Selector

if TYPE_CHECKING:
    from avilla.core.protocol import BaseProtocol

ActionHandler = Callable[["ActionExecutor", NonStandardAction, Relationship], Any]


def action(*action_types: type[NonStandardAction]):
    def decorator(func):
        func.__supported_actions__ = action_types
        return func

    return decorator


class ActionExecutor:
    action_handlers: ClassVar[dict[type[NonStandardAction], Callable[[Self, NonStandardAction, Relationship], Any]]] = {}
    standard_actions: ClassVar[list[StandardAction]] = []
    pattern: ClassVar[Selector | None] = None
    # 给外部调用 match
    # 如果是 None, 表示不对其做约束...并且适用于我们不知道 target 到底是什么的情况.
    # 这适用于与平台数据无关的, 比如说我们可以有个 GetVersion(当然实际中我建议 Version) 的 Action, 他不需要 target.

    def __init_subclass__(cls, pattern: Selector | None = None):
        super().__init_subclass__()
        cls.action_handlers = {}
        cls.standard_actions = []
        for mro in reversed(inspect.getmro(cls)):
            if issubclass(mro, ActionExecutor):
                cls.action_handlers.update(mro.action_handlers)
                standard_sets = set(cls.standard_actions)
                standard_sets.update(mro.standard_actions)
                cls.action_handlers = list(standard_sets)
        members = inspect.getmembers(cls)
        for _, value in members:
            actions: list[type[NonStandardAction]] = getattr(value, "__supported_actions__", [])
            if actions:
                cls.action_handlers.update({action_type: value for action_type in actions})
            if inspect.isclass(value) and issubclass(value, StandardAction):
                standard_sets = set(cls.standard_actions)
                standard_sets.add(value)
                cls.standard_actions = list(standard_sets)
        if pattern is not None:
            cls.pattern = pattern

    def execute(self, relationship: Relationship, action: NonStandardAction):
        handler = self.action_handlers.get(type(action))
        if handler is None:
            raise NotImplementedError(f"Action {type(action)} is not supported.")
        return handler(self, action, relationship)


_P = TypeVar("_P", bound="BaseProtocol")


class ProtocolActionExecutor(ActionExecutor, Generic[_P]):
    protocol: _P

    def __init__(self, protocol: _P) -> None:
        self.protocol = protocol
