from __future__ import annotations

from abc import ABCMeta, abstractmethod
from datetime import datetime
from typing import TYPE_CHECKING

from graia.broadcast.entities.dispatcher import BaseDispatcher
from graia.broadcast.entities.event import Dispatchable

from avilla.core.account import AccountSelector
from avilla.core.context import ctx_protocol, ctx_relationship
from avilla.core.relationship import Relationship

if TYPE_CHECKING:
    from types import TracebackType

    from graia.broadcast.interfaces.dispatcher import DispatcherInterface

    from avilla.core.metadata.model import MetadataModifies
    from avilla.core.utilles.selector import Selector


class AvillaEvent(Dispatchable, metaclass=ABCMeta):
    account: AccountSelector
    time: datetime

    @property
    @abstractmethod
    def ctx(self) -> Selector:
        ...

    # TODO: Metadata in Event


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
