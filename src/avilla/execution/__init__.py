from typing import Any, Generic

from pydantic import BaseModel  # pylint: ignore
from avilla.typing import T_Target, T_Result


class Execution(BaseModel, Generic[T_Target]):
    target: T_Target = None

    def with_target(self, target: T_Target) -> "Execution[T_Target]":
        self.target = target
        return self

    class Config:
        allow_mutation = True


class Result(Generic[T_Result]):
    pass


class Operation(Result[Any], Execution[T_Target]):
    "操作成功返回 None, 否则应抛出错误."
    ...
