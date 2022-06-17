from __future__ import annotations

import typing
from abc import ABCMeta, abstractmethod
from typing import TYPE_CHECKING, Any, Generic, TypeVar

from graia.broadcast.entities.dispatcher import BaseDispatcher
from graia.broadcast.entities.event import Dispatchable

from avilla.core.context import ctx_protocol, ctx_relationship
from avilla.core.relationship import Relationship

if TYPE_CHECKING:
    from datetime import datetime
    from types import TracebackType

    from graia.broadcast.interfaces.dispatcher import DispatcherInterface

    from avilla.core.metadata.model import MetadataModifies
    from avilla.core.resource import Resource
    from avilla.core.selectors import entity as entity_selector
    from avilla.core.selectors import mainline as mainline_selector
    from avilla.core.selectors import request as request_selector
    from avilla.core.utilles.selector import Selector


class AvillaEvent(Dispatchable, metaclass=ABCMeta):
    self: entity_selector
    time: datetime

    _event_meta: dict[str, Any] | None = None

    def __repr__(self) -> str:
        return (
            f"<{self.__class__.__name__}: {' '.join([f'{k}={v.__repr__()}' for k, v in vars(self).items()])}>"
        )

    @classmethod
    def get_ability_id(cls) -> str:
        return f"event::{cls.__name__}"

    @property
    @abstractmethod
    def ctx(self) -> Selector:
        ...

    def with_meta(self, meta: dict[str, Any]):
        self._event_meta = meta
        return self


class RelationshipDispatcher(BaseDispatcher):
    @staticmethod
    async def beforeExecution(interface: DispatcherInterface[AvillaEvent]):
        protocol = ctx_protocol.get()
        if protocol is not None:
            rs = await protocol.get_relationship(interface.event.ctx, interface.event.self)
            token = ctx_relationship.set(rs)
            interface.local_storage["relationship"] = rs
            interface.local_storage["_ctxtoken_rs"] = token

    @staticmethod
    async def afterExecution(
        interface: DispatcherInterface[AvillaEvent],
        exception: Exception | None,
        tb: TracebackType | None,
    ):
        ctx_relationship.reset(interface.local_storage["_ctxtoken_rs"])

    @staticmethod
    async def catch(interface: DispatcherInterface[AvillaEvent]):
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

    @property
    def ctx(self) -> request_selector:
        return self.request

    def __init__(
        self,
        request: request_selector,
        current_self: entity_selector,
        time: datetime | None = None,
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

    @property
    def ctx(self) -> request_selector:
        return self.request

    def __init__(
        self, request: request_selector, current_self: entity_selector, time: datetime | None = None
    ):
        self.request = request
        self.self = current_self
        self.time = time or datetime.now()


class RequestRejected(AvillaEvent):
    request: request_selector

    @property
    def ctx(self) -> request_selector:
        return self.request

    def __init__(
        self, request: request_selector, current_self: entity_selector, time: datetime | None = None
    ):
        self.request = request
        self.self = current_self
        self.time = time or datetime.now()


class RequestIgnored(AvillaEvent):
    request: request_selector

    @property
    def ctx(self) -> request_selector:
        return self.request

    def __init__(
        self, request: request_selector, current_self: entity_selector, time: datetime | None = None
    ):
        self.request = request
        self.self = current_self
        self.time = time or datetime.now()


R = TypeVar("R", bound="Resource")


class ResourceAvailable(AvillaEvent, Generic[R]):
    resource: R

    @property
    def ctx(self) -> R:
        return self.resource

    @property
    def mainline(self):
        return self.resource.mainline

    def __init__(self, resource: R, current_self: entity_selector, time: datetime | None = None):
        self.resource = resource
        self.self = current_self
        self.time = time or datetime.now()


class ResourceUnavailable(AvillaEvent, Generic[R]):
    resource: R

    @property
    def ctx(self) -> R:
        return self.resource

    @property
    def mainline(self):
        return self.resource.mainline

    def __init__(self, resource: R, current_self: entity_selector, time: datetime | None = None):
        self.resource = resource
        self.self = current_self
        self.time = time or datetime.now()


class MetadataModified(AvillaEvent):
    ctx: entity_selector | mainline_selector
    modifies: MetadataModifies
    operator: entity_selector | None = None

    def __init__(
        self,
        ctx: entity_selector | mainline_selector,
        modifies: MetadataModifies,
        current_self: entity_selector,
        operator: entity_selector | None = None,
        time: datetime | None = None,
    ):
        self.ctx = ctx
        self.modifies = modifies
        self.operator = operator
        self.self = current_self
        self.time = time or datetime.now()


class RelationshipCreated(AvillaEvent):
    ctx: mainline_selector | entity_selector
    via: mainline_selector | entity_selector | None
    # 用 via 同时表示两个方向的关系.(自发行为和被动行为)
    # 自发行为就是 None, 被动行为反之

    def __init__(
        self,
        ctx: mainline_selector | entity_selector,
        current_self: entity_selector,
        time: datetime | None = None,
        via: mainline_selector | entity_selector | None = None,
    ):
        self.ctx = ctx
        self.via = via
        self.self = current_self
        self.time = time or datetime.now()


class RelationshipDestroyed(AvillaEvent):
    ctx: mainline_selector | entity_selector
    via: mainline_selector | entity_selector | None

    def __init__(
        self,
        ctx: mainline_selector | entity_selector,
        current_self: entity_selector,
        time: datetime | None = None,
        via: mainline_selector | entity_selector | None = None,
    ):
        self.ctx = ctx
        self.via = via
        self.self = current_self
        self.time = time or datetime.now()
