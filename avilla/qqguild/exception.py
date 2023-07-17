from typing import Optional

from avilla.core.exceptions import (
    HttpRequestError,
    InvalidAuthentication,
    NetworkError as BaseNetworkError,
)

class ActionFailed(HttpRequestError):
    def __init__(self, status: int, body: Optional[dict] = None):
        self.status_code: int = status
        self.body = body or {}
        self.code: Optional[int] = self.body.get("code", None)
        self.message: Optional[str] = self.body.get("message", None)
        self.data: Optional[dict] = self.body.get("data", None)

    def __repr__(self) -> str:
        return (
            f"<ActionFailed: {self.status_code}, code={self.code}, "
            f"message={self.message}, data={self.data}>"
        )


class UnauthorizedException(ActionFailed, InvalidAuthentication):
    pass


class RateLimitException(ActionFailed):
    pass


class NetworkError(BaseNetworkError):
    def __init__(self, msg: Optional[str] = None):
        super().__init__()
        self.msg: Optional[str] = msg
        """错误原因"""

    def __repr__(self):
        return f"<NetWorkError message={self.msg}>"

    def __str__(self):
        return self.__repr__()


class AuditException(Exception):
    """消息审核"""

    def __init__(self, audit_id: str):
        super().__init__()
        self.audit_id = audit_id
