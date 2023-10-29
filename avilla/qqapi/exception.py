from typing import Optional

from avilla.core.exceptions import ActionFailed as BaseActionFailed
from avilla.core.exceptions import HttpRequestError, InvalidAuthentication
from avilla.core.exceptions import NetworkError as BaseNetworkError
from avilla.qqapi.audit import audit_result


class ActionFailed(HttpRequestError, BaseActionFailed):
    def __init__(self, status: int, body: Optional[dict] = None):
        self.body = body or {}
        self.code: Optional[int] = self.body.get("code", None)
        self.message: Optional[str] = self.body.get("message", None)
        self.data: Optional[dict] = self.body.get("data", None)
        super().__init__(status, self.message or "Unknown")

    def __repr__(self) -> str:
        return (
            f"<{self.__class__.__name__}: {self.status}, code={self.code}, "
            f"message={self.message}, data={self.data}>"
        )


class UnauthorizedException(ActionFailed, InvalidAuthentication):
    pass


class RateLimitException(ActionFailed):
    pass


class ApiNotAvailable(ActionFailed):
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

    async def get_audit_result(self, timeout: Optional[float] = None):
        """获取审核结果"""
        return await audit_result.fetch(self.audit_id, timeout or 60)
