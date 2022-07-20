"""Ariadne 的异常定义"""


from avilla.core.exceptions import (
    InvalidAuthentication,
    InvalidOperation,
    ParserException,
)


class InvalidEventTypeDefinition(ParserException):
    """不合法的事件类型定义."""


class InvalidVerifyKey(InvalidAuthentication):
    """无效的 verifyKey 或其配置."""


class AccountNotFound(InvalidAuthentication):
    """未能使用所配置的账号激活 sessionKey, 请检查 mirai_session 配置."""


class InvalidSession(InvalidAuthentication):
    """无效的 sessionKey, 请重新获取."""


class UnVerifiedSession(InvalidAuthentication):
    """尚未验证/绑定的 session."""


class MissingNecessaryArgument(InvalidOperation):
    """应在所提到的参数之中至少传入/使用一个"""


class ConflictItem(InvalidOperation):
    """项冲突/其中一项被重复定义"""
