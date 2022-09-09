from __future__ import annotations

from abc import ABCMeta, abstractmethod
from dataclasses import dataclass
from datetime import datetime
from typing import TYPE_CHECKING, Any, get_origin, get_args

from graia.broadcast.entities.event import Dispatchable
from graia.broadcast.entities.dispatcher import BaseDispatcher

if TYPE_CHECKING:
    from graia.broadcast.interfaces.dispatcher import DispatcherInterface
    from avilla.core.account import AbstractAccount
    from avilla.core.utilles.selector import Selector

    from ..cell import Cell, CellOf


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


@dataclass
class MetadataModify:
    describe: type[Cell] | CellOf
    field: str
    current: Any
    past: Any | None = None


class MetadataModified(AvillaEvent):
    ctx: Selector
    modifies: list[MetadataModify]
    operator: Selector | None = None

    def __init__(
        self,
        ctx: Selector,
        modifies: list[MetadataModify],
        account: AbstractAccount,
        operator: Selector | None = None,
        time: datetime | None = None,
        extra: dict[Any, Any] | None = None,
    ):
        self.ctx = ctx
        self.modifies = modifies
        self.operator = operator
        super().__init__(account, time=time, extra=extra)

    class Dispatcher(BaseDispatcher):
        @staticmethod
        async def catch(interface: DispatcherInterface["MetadataModified"]):
            if get_origin(interface.annotation) is list and get_args(interface.annotation)[0] is MetadataModify:
                return interface.event.modifies


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

    class Dispatcher(BaseDispatcher):
        @staticmethod
        async def catch(interface: DispatcherInterface["RelationshipCreated"]):
            ...


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

    class Dispatcher(BaseDispatcher):
        @staticmethod
        async def catch(interface: DispatcherInterface["RelationshipDestroyed"]):
            ...
