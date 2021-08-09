from typing import Any, Generic

from pydantic import BaseModel

from avilla.entity import Entity, EntityPtr
from avilla.group import Group, GroupPtr
from avilla.typing import T_Result, T_Target


class Execution(BaseModel, Generic[T_Target]):
    target: T_Target = None  # type: ignore

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


def auto_update_forward_refs(cls):
    cls.update_forward_refs(EntityPtr=EntityPtr, Entity=Entity, Group=Group, GroupPtr=GroupPtr)
    return cls
