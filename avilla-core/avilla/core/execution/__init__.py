from typing import Any, Generic

from avilla.core.entity import Entity, EntityPtr
from avilla.core.group import Group, GroupPtr
from avilla.core.typing import T_Result
from pydantic import BaseModel


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


def auto_update_forward_refs(cls):
    cls.update_forward_refs(EntityPtr=EntityPtr, Entity=Entity, Group=Group, GroupPtr=GroupPtr)
    return cls
