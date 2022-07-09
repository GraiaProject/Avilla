from typing import (
    TYPE_CHECKING,
    Any,
    Callable,
    Generic,
    Protocol,
    TypeVar,
    runtime_checkable,
)

if TYPE_CHECKING:
    from contextlib import AbstractAsyncContextManager

    from avilla.core.protocol import BaseProtocol
    from avilla.core.relationship import RelationshipExecutor


TProtocol = TypeVar("TProtocol", bound="BaseProtocol")

ActionMiddleware = Callable[["RelationshipExecutor"], "AbstractAsyncContextManager[None]"]

_T = TypeVar("_T", contravariant=True)


@runtime_checkable
class Ensureable(Protocol, Generic[_T]):
    def ensure(self, interact: _T) -> Any:
        ...
