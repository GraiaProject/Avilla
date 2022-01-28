import typing
from contextvars import Token
from dataclasses import dataclass
from datetime import datetime
from types import TracebackType
from typing import Dict, List, Optional, Union

from graia.broadcast.entities.dispatcher import BaseDispatcher
from graia.broadcast.entities.event import Dispatchable
from graia.broadcast.interfaces.dispatcher import DispatcherInterface

from avilla.core.relationship import Relationship
from avilla.core.selectors import entity as entity_selector
from avilla.core.selectors import mainline as mainline_selector
from avilla.core.selectors import request as request_selector
from avilla.core.selectors import resource as resource_selector
from avilla.core.typing import METADATA_VALUE

from ..context import ctx_protocol, ctx_relationship


class AvillaEvent(Dispatchable):
    ctx: entity_selector

    self: entity_selector
    time: datetime

    def __repr__(self) -> str:
        return (
            f"<{self.__class__.__name__}: {' '.join([f'{k}={v.__repr__()}' for k, v in vars(self).items()])}>"
        )

    @classmethod
    def get_ability_id(cls) -> str:
        return f"event::{cls.__name__}"


_Dispatcher_Tokens: "Dict[int, Token[Relationship]]" = {}


class RelationshipDispatcher(BaseDispatcher):  # Avilla 将自动注入...哦, 看起来没这个必要.
    @staticmethod
    async def beforeExecution(interface: "DispatcherInterface[AvillaEvent]"):
        rs = await ctx_protocol.get().get_relationship(interface.event.ctx)
        token = ctx_relationship.set(rs)
        interface.local_storage["_ctxtoken_rs"] = token

    @staticmethod
    async def afterExecution(
        interface: "DispatcherInterface",
        exception: Optional[Exception],
        tb: Optional[TracebackType],
    ):
        ctx_relationship.reset(interface.local_storage["_ctxtoken_rs"])

    @staticmethod
    async def catch(interface: "DispatcherInterface"):
        if typing.get_origin(interface.annotation) is Relationship or interface.annotation is Relationship:
            return ctx_relationship.get()


class RequestEvent(AvillaEvent):
    request: request_selector

    acceptable: bool = True
    rejectable: bool = True
    ignorable: bool = False

    @property
    def mainline(self):
        return self.request.get_mainline()

    def __init__(
        self,
        request: request_selector,
        current_self: entity_selector,
        time: datetime = None,
        acceptable: bool = True,
        rejectable: bool = True,
        ignorable: bool = False,
    ):
        self.request = request
        self.acceptable = acceptable
        self.rejectable = rejectable
        self.ignorable = ignorable
        self.self = current_self
        self.time = time or datetime.now()


class RequestAccepted(AvillaEvent):
    request: request_selector

    def __init__(
        self,
        request: request_selector,
        current_self: entity_selector,
        time: datetime = None,
    ):
        self.request = request
        self.self = current_self
        self.time = time or datetime.now()


class RequestRejected(AvillaEvent):
    request: request_selector

    def __init__(
        self,
        request: request_selector,
        current_self: entity_selector,
        time: datetime = None,
    ):
        self.request = request
        self.self = current_self
        self.time = time or datetime.now()


class RequestIgnored(AvillaEvent):
    request: request_selector

    def __init__(
        self,
        request: request_selector,
        current_self: entity_selector,
        time: datetime = None,
    ):
        self.request = request
        self.self = current_self
        self.time = time or datetime.now()


class ResourceAvailable(AvillaEvent):
    resource: resource_selector
    operator: Optional[entity_selector] = None

    @property
    def mainline(self):
        return self.resource.get_mainline()

    def __init__(
        self,
        resource: resource_selector,
        operator: Optional[entity_selector],  # 本来应该默认 None, 但是 current_self 不太行....
        current_self: entity_selector,
        time: datetime = None,
    ):
        self.resource = resource
        self.operator = operator
        self.self = current_self
        self.time = time or datetime.now()


class ResourceUnavailable(AvillaEvent):
    resource: resource_selector
    operator: Optional[entity_selector] = None

    @property
    def mainline(self):
        return self.resource.get_mainline()

    def __init__(
        self,
        resource: resource_selector,
        operator: Optional[entity_selector],
        current_self: entity_selector,
        time: datetime = None,
    ):
        self.resource = resource
        self.operator = operator
        self.self = current_self
        self.time = time or datetime.now()


class MetadataChanged(AvillaEvent):
    ctx: Union[entity_selector, mainline_selector]
    meta: str
    op: str
    value: METADATA_VALUE

    def __init__(
        self,
        ctx: Union[entity_selector, mainline_selector],
        meta: str,
        op: str,
        value: METADATA_VALUE,
        current_self: entity_selector,
        time: datetime = None,
    ):
        self.ctx = ctx
        self.meta = meta
        self.op = op
        self.value = value
        self.self = current_self
        self.time = time or datetime.now()


@dataclass
class PermissionChangeInfo:
    pass


@dataclass
class RankChanged(PermissionChangeInfo):
    past: str
    current: str


# TODO: 更完备的权限变化描述方式, 属权限系统部分.


class EntityPermissionChanged(AvillaEvent):
    entity: entity_selector
    modifies: List[PermissionChangeInfo]

    def __init__(
        self,
        entity: entity_selector,
        modifies: List[PermissionChangeInfo],
        current_self: entity_selector,
        time: datetime = None,
    ):
        self.entity = entity
        self.modifies = modifies
        self.self = current_self
        self.time = time or datetime.now()


class RelationshipCreated(AvillaEvent):
    ctx: Union[mainline_selector, entity_selector]
    via: Union[mainline_selector, entity_selector, None]  # 我暂时想不到为什么要有了 via 再多一个 operator 的理由.

    def __init__(
        self,
        ctx: Union[mainline_selector, entity_selector],
        via: Union[mainline_selector, entity_selector, None],
        current_self: entity_selector,
        time: datetime = None,
    ):
        self.ctx = ctx
        self.via = via
        self.self = current_self
        self.time = time or datetime.now()


class RelationshipDestroyed(AvillaEvent):
    ctx: Union[mainline_selector, entity_selector]
    via: Union[mainline_selector, entity_selector, None]

    def __init__(
        self,
        ctx: Union[mainline_selector, entity_selector],
        via: Union[mainline_selector, entity_selector, None],
        current_self: entity_selector,
        time: datetime = None,
    ):
        self.ctx = ctx
        self.via = via
        self.self = current_self
        self.time = time or datetime.now()
