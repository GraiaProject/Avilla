from typing import TYPE_CHECKING, Optional

from pydantic.main import BaseModel


from avilla.entity import Entity

from . import Operation


class RequestHandle(BaseModel, Operation):
    ...


class RequestApprove(RequestHandle):
    ...


class RequestDeny(RequestHandle):
    reason: Optional[str] = None
    block: bool = False


class RequestIgnore(RequestHandle):
    block: bool = False
