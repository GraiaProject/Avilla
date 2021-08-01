from typing import Type, Union
from graia.broadcast.builtin.decorators import Depend
from avilla.group import Group
from avilla.entity import Entity
from avilla.relationship import Relationship
from graia.broadcast.exceptions import ExecutionStop
from avilla.profile import BaseProfile
from .rs import *


def useCtx(*ctxs: Union[Type[Group], Type[Entity]]):
    def wrapper(rs: Relationship):
        for ctx in ctxs:
            if isinstance(rs.entity_or_group, ctx):
                return
        else:
            raise ExecutionStop

    return Depend(wrapper)


def useCtxProfile(ctx_type: Union[Type[Group], Type[Entity]], profile_type: Type[BaseProfile]):
    def wrapper(rs: Relationship):
        if isinstance(rs.entity_or_group, ctx_type):
            if isinstance(rs.entity_or_group.profile, profile_type):
                return
            raise ExecutionStop

    return Depend(wrapper)


def useCtxId(ctx_type: Union[Type[Group], Type[Entity]], id: str):
    def wrapper(rs: Relationship):
        if isinstance(rs.entity_or_group, ctx_type):
            if rs.entity_or_group.id == id:
                return
            raise ExecutionStop

    return Depend(wrapper)
