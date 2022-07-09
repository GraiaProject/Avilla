from __future__ import annotations

import typing
from abc import ABCMeta, abstractmethod
from typing import TYPE_CHECKING, Any, Generic, Literal, TypeVar

from graia.broadcast.entities.dispatcher import BaseDispatcher
from graia.broadcast.entities.event import Dispatchable

from avilla.core.account import AccountSelector
from avilla.core.context import ctx_protocol, ctx_relationship
from avilla.core.relationship import Relationship
from avilla.core.request import Request
from avilla.core.resource import Resource

if TYPE_CHECKING:
    from datetime import datetime
    from types import TracebackType

    from graia.broadcast.interfaces.dispatcher import DispatcherInterface

    from avilla.core.metadata.model import MetadataModifies
    from avilla.core.utilles.selector import Selector


class AvillaEvent(Dispatchable, metaclass=ABCMeta):
    account: AccountSelector
    time: datetime

    meta: dict[str, Any] | None = None

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__}: {' '.join([f'{k}={v!r}' for k, v in vars(self).items()])}>"

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
            account = protocol.get_account(interface.event.account)
            if account is None:
                raise ValueError(f"Account {interface.event.account} not found")
            rs = await account.get_relationship(interface.event.ctx)
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
        if interface.annotation is Relationship:
            return ctx_relationship.get()


class RequestEvent(AvillaEvent):
    request: Request

    @property
    def mainline(self):
        return self.request.mainline

    @property
    def ctx(self):
        return self.request.sender

    def __init__(
        self,
        request: Request,
        time: datetime | None = None,
    ):
        self.request = request
        self.account = request.account
        self.time = time or request.time


class RequestAccepted(AvillaEvent):
    request: Request

    @property
    def ctx(self):
        return self.request.sender

    def __init__(
        self,
        request: Request,
        time: datetime | None = None,
    ):
        self.request = request
        self.account = request.account
        self.time = time or request.time


class RequestRejected(AvillaEvent):
    request: Request

    @property
    def ctx(self):
        return self.request.sender

    def __init__(
        self,
        request: Request,
        time: datetime | None = None,
    ):
        self.request = request
        self.account = request.account
        self.time = time or request.time


class RequestIgnored(AvillaEvent):
    request: Request

    @property
    def ctx(self):
        return self.request.sender

    def __init__(
        self,
        request: Request,
        time: datetime | None = None,
    ):
        self.request = request
        self.account = request.account
        self.time = time or request.time


class RequestCancelled(AvillaEvent):
    request: Request

    @property
    def ctx(self):
        return self.request.sender

    def __init__(
        self,
        request: Request,
        time: datetime | None = None,
    ):
        self.request = request
        self.account = request.account
        self.time = time or request.time


R = TypeVar("R", bound=Resource)


class ResourceAvailable(AvillaEvent, Generic[R]):
    resource: R

    @property
    def ctx(self):
        return self.resource.to_selector().set_referent(self.resource)

    @property
    def mainline(self):
        return self.resource.mainline

    def __init__(
        self,
        resource: R,
        account: AccountSelector,
        time: datetime | None = None,
    ):
        self.resource = resource
        self.account = account
        self.time = time or datetime.now()


class ResourceUnavailable(AvillaEvent, Generic[R]):
    resource: R

    @property
    def ctx(self):
        return self.resource.to_selector().set_referent(self.resource)

    @property
    def mainline(self):
        return self.resource.mainline

    def __init__(
        self,
        resource: R,
        account: AccountSelector,
        time: datetime | None = None,
    ):
        self.resource = resource
        self.account = account
        self.time = time or datetime.now()


class MetadataModified(AvillaEvent):
    ctx: Selector
    modifies: MetadataModifies
    operator: Selector | None = None

    def __init__(
        self,
        ctx: Selector,
        modifies: MetadataModifies,
        account: AccountSelector,
        operator: Selector | None = None,
        time: datetime | None = None,
    ):
        self.ctx = ctx
        self.modifies = modifies
        self.operator = operator
        self.account = account
        self.time = time or datetime.now()


class RelationshipCreated(AvillaEvent):
    ctx: Selector
    via: Selector | None
    # 用 via 同时表示两个方向的关系.(自发行为和被动行为)
    # 自发行为就是 None, 被动行为反之

    def __init__(
        self,
        ctx: Selector,
        account: AccountSelector,
        time: datetime | None = None,
        via: Selector | None = None,
    ):
        self.ctx = ctx
        self.via = via
        self.account = account
        self.time = time or datetime.now()


class RelationshipDestroyed(AvillaEvent):
    ctx: Selector
    via: Selector | None

    def __init__(
        self,
        ctx: Selector,
        account: AccountSelector,
        time: datetime | None = None,
        via: Selector | None = None,
    ):
        self.ctx = ctx
        self.via = via
        self.account = account
        self.time = time or datetime.now()
