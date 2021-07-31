from enum import IntEnum
from typing import TYPE_CHECKING, Any, Generic, TypeVar

from pydantic.main import BaseModel


T_Target = TypeVar("T_Target")


class Execution(Generic[T_Target]):
    target: T_Target = None


T_Result = TypeVar("T_Result")


class Result(Generic[T_Result]):
    pass


class Operation(Result[None], Execution[Any]):
    "操作成功返回 None, 否则应抛出错误."
    ...
