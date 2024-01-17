from __future__ import annotations

import functools
from contextvars import copy_context
from typing import Callable

from .typing import P, R


def standalone_context(func: Callable[P, R]) -> Callable[P, R]:
    @functools.wraps(func)
    def wrapper(*args: P.args, **kwargs: P.kwargs) -> R:
        return copy_context().run(func, *args, **kwargs)

    return wrapper
