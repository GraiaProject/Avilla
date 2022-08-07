from typing import (
    TYPE_CHECKING,
    Any,
    Callable,
    Coroutine,
    Generic,
    Protocol,
    TypeVar,
    runtime_checkable,
)

if TYPE_CHECKING:
    from avilla.core.action.extension import ActionExtension
    from avilla.core.protocol import BaseProtocol
    from avilla.core.relationship import RelationshipExecutor

TProtocol = TypeVar("TProtocol", bound="BaseProtocol")

ActionExtensionImpl = Callable[
    ["RelationshipExecutor", "ActionExtension", dict[str, Any] | None], Coroutine[None, None, Any]
]


_T = TypeVar("_T", contravariant=True)


@runtime_checkable
class Ensureable(Protocol, Generic[_T]):
    def ensure(self, interact: _T) -> Any:
        ...
