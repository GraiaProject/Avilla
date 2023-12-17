from __future__ import annotations

from avilla.core.exceptions import InvalidAuthentication


class InvalidToken(InvalidAuthentication):
    """无效的 Token"""


class WrongFragment(Exception):
    """skip 就完事儿"""
