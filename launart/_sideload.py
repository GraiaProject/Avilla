from __future__ import annotations

from collections import ChainMap
from typing import TYPE_CHECKING, Any, Dict, TypeVar, cast

if TYPE_CHECKING:
    from launart.manager import U_ManagerStage


class Override:
    def __init__(self, source: Any, additional: Dict[str, Any]):
        self.__source = source
        self.__additional = additional

    @property
    def source(self):
        return self.__source

    @property
    def __data(self):
        return ChainMap(self.__additional, vars(self.__source))

    def __getattr__(self, item):
        if item not in self.__data:
            raise AttributeError(f"'{self.__source.__class__.__name__}' object has no attribute '{item}'")
        return self.__data[item]


T = TypeVar("T")


def override(source: T, additional: Dict[str, Any]) -> T:
    return cast(T, Override(source, additional))


class FutureMark:
    id: str
    stage: U_ManagerStage | None = None

    def __init__(self, id: str, stage: U_ManagerStage | None = None) -> None:
        self.id = id
        self.stage = stage

    def __call__(self, _) -> Any:
        pass
