import json
from typing import Optional, Mapping

from avilla.core.exceptions import ActionFailed as BaseActionFailed
from avilla.core.exceptions import HttpRequestError, InvalidAuthentication
from avilla.core.exceptions import NetworkError as BaseNetworkError
from avilla.qqapi.audit import audit_result


class ActionFailed(HttpRequestError, BaseActionFailed):
    def __init__(self, status: int, headers: Mapping, response: Optional[str] = None):
        self.body = {}
        self.headers = headers
        if response:
            try:
                self.body = json.loads(response)
            except json.JSONDecodeError:
                pass
        super().__init__(status, self.body.get("message", "Unknown Error"))

    @property
    def code(self) -> Optional[int]:
        return None if self.body is None else self.body.get("code", None)

    @property
    def message(self) -> Optional[str]:
        return None if self.body is None else self.body.get("message", None)

    @property
    def data(self) -> Optional[dict]:
        return None if self.body is None else self.body.get("data", None)

    @property
    def trace_id(self) -> Optional[str]:
        return self.headers.get("X-Tps-trace-ID", None)

    def __repr__(self) -> str:
        args = ("code", "message", "data", "trace_id")
        return (
            f"<{self.__class__.__name__}: {self.status}, "
            + ", ".join(f"{k}={v}" for k in args if (v := getattr(self, k)) is not None)
            + ">"
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
