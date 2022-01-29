from datetime import datetime, timedelta
from typing import (
    TYPE_CHECKING,
    AsyncContextManager,
    Callable,
    Dict,
    List,
    TypeVar,
    Union,
)

if TYPE_CHECKING:
    from avilla.core.execution import Execution
    from avilla.core.protocol import BaseProtocol
    from avilla.core.relationship import Relationship


TProtocol = TypeVar("TProtocol", bound="BaseProtocol")

TExecutionMiddleware = Callable[["Relationship", "Execution"], AsyncContextManager[None]]

CONST_TYPES = Union[str, bool, int, float, datetime, timedelta, None]
STRUCTURE = Union[CONST_TYPES, List[CONST_TYPES], Dict[str, CONST_TYPES]]
