"""Ariadne 的异常定义"""


from avilla.core.exceptions import InvalidOperation, RemoteError, UnsupportedOperation


class AriadneConfigurationError(ValueError):
    """配置 Ariadne 时给出的参数包含有错误."""


class InvalidArgument(InvalidOperation):
    """应在所提到的参数之中至少传入/使用一个"""


class UnsupportedArgument(UnsupportedOperation):
    """不支持的参数"""


ERRORS: dict[int, type[Exception]] = {
    # 1xxxx: Request Error
    10001: InvalidOperation,
    10002: UnsupportedOperation,
    10003: InvalidArgument,
    10004: UnsupportedArgument,
    10005: NotImplementedError,
    10006: InvalidArgument,
    10007: InvalidArgument,
    # 2xxxx: HandlerError
    20001: RemoteError,
    20002: RemoteError,
}


def get_error(retcode: int):
    if retcode == 0:
        return
    if retcode in ERRORS:
        return ERRORS[retcode]
    return RemoteError
