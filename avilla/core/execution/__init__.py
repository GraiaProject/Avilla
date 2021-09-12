from typing import Any, Generic

from pydantic import BaseModel

from avilla.core.typing import T_Result


class Execution(BaseModel):
    _auto_detect_target: bool = False  # for detect target automatically

    @classmethod
    def get_ability_id(cls) -> str:
        return f"execution::{cls.__name__}"

    class Config:
        allow_mutation = True


class Result(Generic[T_Result]):
    pass


class Operation(Result[Any], Execution):
    "操作成功返回 None, 否则应抛出错误."
    ...
