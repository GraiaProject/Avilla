from dataclasses import dataclass

from avilla.entity import Entity
from . import Operation, TargetTypes
from typing import Optional


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
