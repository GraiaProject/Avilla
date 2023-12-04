from __future__ import annotations

import functools
from contextvars import copy_context
from typing import Callable, TypeVar

from ryanvk.typing import P, R

T = TypeVar("T")


def standalone_context(func: Callable[P, R]) -> Callable[P, R]:
    @functools.wraps(func)
    def wrapper(*args: P.args, **kwargs: P.kwargs) -> R:
        cx = copy_context()
        # copy_context 是浅拷贝，只要约束 assign/initizate 就能完美运作。

        return cx.run(func, *args, **kwargs)

    return wrapper
