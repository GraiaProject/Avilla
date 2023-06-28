from typing import Any, Protocol, TypeVar, runtime_checkable

# if TYPE_CHECKING:
#     pass

"""
TProtocol = TypeVar("TProtocol", bound="BaseProtocol")


ActionExtensionImpl = Callable[
    ["RelationshipExecutor", "ActionExtension", dict[str, Any] | None], Coroutine[None, None, Any]
]
"""

_T = TypeVar("_T", contravariant=True)


@runtime_checkable
class Ensureable(Protocol[_T]):
    def ensure(self, interact: _T) -> Any:
        ...
