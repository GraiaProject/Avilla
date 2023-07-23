from __future__ import annotations

from typing import TYPE_CHECKING, Any, Dict, TypeVar, cast

if TYPE_CHECKING:
    from launart.status import U_ManagerStage


class Override:
    def __init__(self, source: Any, additional: Dict[str, Any]):
        self.__source = source
        self.__additional = additional

    @property
    def source(self):
        return self.__source

    def __getattr__(self, item):
        if item in self.__additional:
            return self.__additional[item]
        return getattr(self.__source, item)


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
