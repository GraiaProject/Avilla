from __future__ import annotations

from abc import ABCMeta, abstractmethod
from datetime import datetime
from typing import TYPE_CHECKING, Any

from graia.broadcast.entities.event import Dispatchable

if TYPE_CHECKING:
    from avilla.core.account import AbstractAccount
    from avilla.core.metadata.model import MetadataModifies
    from avilla.core.utilles.selector import Selector


class AvillaEvent(Dispatchable, metaclass=ABCMeta):
    account: AbstractAccount
    time: datetime

    extra: dict[Any, Any]

    def __init__(
        self, account: AbstractAccount, *, extra: dict[Any, Any] | None = None, time: datetime | None = None
    ) -> None:
        self.account = account
        self.extra = extra or {}
        self.time = time or datetime.now()

    @property
    @abstractmethod
    def ctx(self) -> Selector:
        ...

    def get_via(self) -> Selector | None:
        ...


class MetadataModified(AvillaEvent):
    ctx: Selector
    modifies: MetadataModifies
    operator: Selector | None = None

    def __init__(
        self,
        ctx: Selector,
        modifies: MetadataModifies,
        account: AbstractAccount,
        operator: Selector | None = None,
        time: datetime | None = None,
        extra: dict[Any, Any] | None = None,
    ):
        self.ctx = ctx
        self.modifies = modifies
        self.operator = operator
        super().__init__(account, time=time, extra=extra)


class RelationshipCreated(AvillaEvent):
    ctx: Selector
    via: Selector | None
    # 用 via 同时表示两个方向的关系.(自发行为和被动行为)
    # 自发行为就是 None, 被动行为反之

    def __init__(
        self,
        ctx: Selector,
        account: AbstractAccount,
        time: datetime | None = None,
        via: Selector | None = None,
    ):
        self.ctx = ctx
        self.via = via
        super().__init__(account, time=time)

    def get_via(self) -> Selector | None:
        return self.via


class RelationshipDestroyed(AvillaEvent):
    ctx: Selector
    via: Selector | None

    def __init__(
        self,
        ctx: Selector,
        account: AbstractAccount,
        time: datetime | None = None,
        via: Selector | None = None,
    ):
        self.ctx = ctx
        self.via = via
        super().__init__(account, time=time)

    def get_via(self) -> Selector | None:
        return self.via
