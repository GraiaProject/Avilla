from collections.abc import Callable
from typing import TYPE_CHECKING, Any, Generic, Protocol, TypeVar, runtime_checkable

if TYPE_CHECKING:
    from contextlib import AbstractAsyncContextManager

    from avilla.core.execution import Execution
    from avilla.core.protocol import BaseProtocol
    from avilla.core.relationship import Relationship


TProtocol = TypeVar("TProtocol", bound="BaseProtocol")

TExecutionMiddleware = Callable[["Relationship", "Execution"], "AbstractAsyncContextManager[None]"]

_T = TypeVar("_T", contravariant=True)


@runtime_checkable
class Ensureable(Protocol, Generic[_T]):
    def ensure(self, interact: _T) -> Any:
        ...
