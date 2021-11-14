from typing import TYPE_CHECKING, TypeVar

if TYPE_CHECKING:
    from .service import Service
    from .policy import Policy
    from .schema import Schema
    from .activity import Activity

M = TypeVar('M', bound="Schema")
P = TypeVar('P', bound="Policy")
S = TypeVar('S', bound="Service")
A = TypeVar('A', bound="Activity")
