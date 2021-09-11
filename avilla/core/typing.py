from avilla.core.contactable import Contactable
from typing import TYPE_CHECKING, AsyncContextManager, Callable, Literal, TypeVar, Union

if TYPE_CHECKING:
    from avilla.core.builtins.profile import GroupProfile
    from avilla.core.execution import Execution
    from avilla.core.profile import BaseProfile
    from avilla.core.protocol import BaseProtocol
    from avilla.core.provider import Provider
    from avilla.core.relationship import Relationship


T_Protocol = TypeVar("T_Protocol", bound="BaseProtocol")
T_Config = TypeVar("T_Config")
T_GroupProfile = TypeVar("T_GroupProfile", bound="GroupProfile", covariant=True)
T_Profile = TypeVar("T_Profile", bound="BaseProfile", covariant=True)
T_Result = TypeVar("T_Result")
T_Target = TypeVar("T_Target", Contactable, str, Literal[None])
T_Provider = TypeVar("T_Provider", bound="Provider")
T_Receive = TypeVar("T_Receive")
T_Value = TypeVar("T_Value")
T_Origin = TypeVar("T_Origin")


# Service: may need to be remade
T_Connection = TypeVar("T_Connection")

T_ExecMW = Callable[["Relationship[T_Profile]", "Execution"], AsyncContextManager[None]]
U_Target = Union[Contactable, str, Literal[None]]
