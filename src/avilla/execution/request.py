from dataclasses import dataclass
from typing import Optional

from avilla.entity import Entity

from . import Operation, TargetTypes


@dataclass
class RequestHandle(Operation):
    target_type = TargetTypes.CTX | TargetTypes.RS


@dataclass
class RequestApprove(RequestHandle):
    ...


@dataclass
class RequestDeny(RequestHandle):
    reason: Optional[str] = None
    block: bool = False


@dataclass
class RequestIgnore(RequestHandle):
    block: bool = False
