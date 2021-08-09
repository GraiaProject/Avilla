from typing import Optional

from . import Operation, auto_update_forward_refs


@auto_update_forward_refs
class RequestHandle(Operation[str]):
    ...


@auto_update_forward_refs
class RequestApprove(RequestHandle):
    def __init__(self, request_id: str) -> None:
        super().__init__(target=request_id)


@auto_update_forward_refs
class RequestDeny(RequestHandle):
    reason: Optional[str] = None
    block: bool = False

    def __init__(
        self, request_id: str, *, reason: Optional[str] = None, block: bool = False
    ) -> None:
        super().__init__(target=request_id, reason=reason, block=block)


@auto_update_forward_refs
class RequestIgnore(RequestHandle):
    block: bool = False

    def __init__(self, request_id: str, *, block: bool = False) -> None:
        super().__init__(target=request_id, block=block)
