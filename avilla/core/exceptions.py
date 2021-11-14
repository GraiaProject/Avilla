class InaccessibleInterface(Exception):
    pass


class NetworkException(Exception):
    pass


class HttpRequestException(NetworkException):
    status: int
    reason: str

    def __init__(self, status: int, reason: str) -> None:
        self.status = status
        self.reason = reason

    def __repr__(self) -> str:
        return f"<HttpRequestException status={self.status} reason={self.reason}>"


class ParserException(Exception):  # 解析器错误..我希望你永远不会用到这个
    pass


class ExecutionException(Exception):
    pass


class OperationFailed(ExecutionException):
    pass


class InvalidAuthentication(Exception):
    pass


class UnsupportedOperation(Exception):
    pass


class AccountMuted(Exception):
    pass


class AccountDeleted(Exception):
    pass


class TooLongMessage(Exception):
    pass


class UnknownTarget(Exception):
    pass


class ContextException(Exception):
    pass
