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


T_Protocol = TypeVar("T_Protocol", bound="BaseProtocol")
T_Config = TypeVar("T_Config")
T_Result = TypeVar("T_Result")

# Service: may need to be remade
T_Connection = TypeVar("T_Connection")

T_ExecMW = Callable[["Relationship", "Execution"], AsyncContextManager[None]]

CONST_TYPES = Union[str, bool, int, float, datetime, timedelta, None]
METADATA_VALUE = Union[CONST_TYPES, List[CONST_TYPES], Dict[str, CONST_TYPES]]
