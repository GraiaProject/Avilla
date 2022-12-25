class InaccessibleInterface(Exception):
    pass


class NetworkError(Exception):
    pass


class HttpRequestError(NetworkError):
    status: int
    reason: str

    def __init__(self, status: int, reason: str) -> None:
        self.status = status
        self.reason = reason

    def __repr__(self) -> str:
        return f"<HttpRequestException status={self.status} reason={self.reason}>"


class ParserException(Exception):  # 解析器错误..我希望你永远不会用到这个
    pass


class ActionFailed(Exception):
    pass


class InvalidAuthentication(Exception):
    pass


class UnsupportedOperation(ActionFailed):
    pass


class InvalidOperation(ActionFailed):
    pass


class AccountMuted(Exception):
    pass


class AccountDeleted(Exception):
    pass


class TooLongMessage(Exception):
    pass


class UnknownTarget(Exception):
    pass


class ContextError(Exception):
    pass


class RemoteError(Exception):
    pass


class UnknownError(Exception):
    """其他错误"""


class DeprecatedError(Exception):
    """该接口已弃用."""


def permission_error_message(operator: str, current: str, required: list[str]):
    return (
        f"missing permission: {operator} required "
        + " or ".join(f'"{i}"' for i in required)
        + f" but current is {current}"
    )
