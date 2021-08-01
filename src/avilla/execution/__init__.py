from enum import IntEnum
from typing import TYPE_CHECKING, Any, Generic, TypeVar

from pydantic import BaseModel


T_Target = TypeVar("T_Target")


class Execution(BaseModel, Generic[T_Target]):
    target: T_Target = None

    def with_target(self, target: T_Target) -> "Execution[T_Target]":
        self.target = target
        return self

    class Config:
        allow_mutation = True


T_Result = TypeVar("T_Result")


class Result(Generic[T_Result]):
    pass


class Operation(Result[None], Execution[T_Target]):
    "操作成功返回 None, 否则应抛出错误."
    ...
