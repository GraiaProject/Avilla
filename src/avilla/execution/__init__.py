from dataclasses import dataclass
from enum import Enum
from typing import Generic, TypeVar


class TargetTypes(Enum):
    NONE = 0b000000
    CTX = 0b000011
    PROTOCOL = 0b000100
    ENTITY = 0b000001
    GROUP = 0b000010
    RS = 0b001000
    RSMEMBER = 0b010000
    MSG = 0b100000


@dataclass
class Execution:
    target: TargetTypes


T_Result = TypeVar("T_Result")


@dataclass
class Result(Generic[T_Result], Execution):
    pass


@dataclass
class Operation(Result[None]):
    "操作成功返回 None, 否则应抛出错误."
    ...
