from typing import Any, Generic, TypeVar

from pydantic import BaseModel


class Execution(BaseModel):
    pass


R = TypeVar("R")


class Result(Generic[R]):
    pass


class Operation(Result[Any], Execution):
    "操作成功返回 None, 否则应抛出错误."
    ...
