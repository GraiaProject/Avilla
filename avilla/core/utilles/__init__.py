from __future__ import annotations

from collections.abc import Callable
from typing import TYPE_CHECKING, Any, Generic, TypeVar

if TYPE_CHECKING:
    from ..context import Context
    from ..trait.context import Artifacts

_T = TypeVar("_T")
_R_co = TypeVar("_R_co", covariant=True)


def identity(obj: Any) -> str:
    return obj.__name__ if isinstance(obj, type) else obj.__class__.__name__


class classproperty(Generic[_R_co]):
    fget: classmethod[_R_co]

    def __init__(self, fget: Callable[[Any], _R_co] | classmethod[_R_co]) -> None:
        if not isinstance(fget, classmethod):
            fget = classmethod(fget)

        self.fget = fget

    def __get__(self, __obj: _T, __type: type[_T] | None = None, /) -> _R_co:
        return self.fget.__get__(__obj, __type)()


def handle_visible(artifacts: Artifacts, context: Context):
    from ..trait.signature import VisibleConf

    return [
        artifacts,
        *[v for k, v in artifacts.items() if isinstance(k, VisibleConf) and k.checker(context)],
    ]
