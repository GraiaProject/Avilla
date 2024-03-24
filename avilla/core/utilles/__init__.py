from __future__ import annotations

from collections.abc import Callable
from typing import Any, Generic, TypeVar

_T = TypeVar("_T")
_R_co = TypeVar("_R_co", covariant=True)


def identity(obj: Any) -> str:
    return obj.__name__ if isinstance(obj, type) else obj.__class__.__name__


class classproperty(Generic[_T, _R_co]):
    fget: tuple[classmethod[_T, [], _R_co]]

    def __init__(self, fget: Callable[[Any], _R_co] | classmethod[_T, [], _R_co]) -> None:
        if not isinstance(fget, classmethod):
            fget = classmethod(fget)

        self.fget = (fget,)

    def __get__(self, __obj: _T, __type: type[_T] | None = None, /) -> _R_co:
        return self.fget[0].__get__(__obj, __type)()


class cachedstatic(Generic[_T, _R_co]):
    fget: tuple[staticmethod[[], _R_co]]
    res: _R_co | None = None

    def __init__(self, fget: Callable[[], _R_co] | staticmethod[[], _R_co]) -> None:
        if not isinstance(fget, staticmethod):
            fget = staticmethod(fget)

        self.fget = (fget,)

    def __get__(self, __obj: _T, __type: type[_T] | None = None, /) -> _R_co:
        if self.res is not None:
            return self.res

        self.res = self.fget[0].__get__(__obj, __type)()
        return self.res  # type: ignore
