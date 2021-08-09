from typing import TYPE_CHECKING, Literal, TypeVar

if TYPE_CHECKING:
    from avilla.builtins.profile import GroupProfile
    from avilla.entity import Entity, EntityPtr
    from avilla.group import Group
    from avilla.profile import BaseProfile
    from avilla.protocol import BaseProtocol
    from avilla.provider import Provider


T_Protocol = TypeVar("T_Protocol", bound="BaseProtocol")
T_Config = TypeVar("T_Config")
T_GroupProfile = TypeVar("T_GroupProfile", bound="GroupProfile", covariant=True)
T_Profile = TypeVar("T_Profile", bound="BaseProfile", covariant=True)
T_Result = TypeVar("T_Result")
T_Target = TypeVar("T_Target", "Entity", "Group", "EntityPtr", str, Literal[None])
T_Provider = TypeVar("T_Provider", bound="Provider")
T_Receive = TypeVar("T_Receive")
T_Value = TypeVar("T_Value")
T_Origin = TypeVar("T_Origin")


# Service: may need to be remade
T_Connection = TypeVar("T_Connection")
