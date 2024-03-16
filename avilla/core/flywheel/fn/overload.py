from __future__ import annotations

from typing import TYPE_CHECKING, Callable, Generic, TypeVar

from typing_extensions import final

if TYPE_CHECKING:
    from .record import FnRecord

TOverload = TypeVar("TOverload", bound="FnOverload", covariant=True)
TCallValue = TypeVar("TCallValue")
TCollectValue = TypeVar("TCollectValue")
TSignature = TypeVar("TSignature")


class FnOverload(Generic[TSignature, TCollectValue, TCallValue]):
    def __init__(self, name: str) -> None:
        self.name = name

    @final
    def dig(self, record: FnRecord, call_value: TCallValue, *, name: str | None = None) -> dict[Callable, None]:
        name = name or self.name
        if name not in record.scopes:
            raise NotImplementedError("cannot lookup any implementation with given arguments")

        return self.harvest(record.scopes[name], call_value)

    @final
    def lay(self, record: FnRecord, collect_value: TCollectValue, implement: Callable, *, name: str | None = None):
        name = name or self.name
        if name not in record.scopes:
            record.scopes[name] = {}

        collection = self.collect(record.scopes[name], self.digest(collect_value))
        collection[implement] = None

    def digest(self, collect_value: TCollectValue) -> TSignature:
        raise NotImplementedError

    def collect(self, scope: dict, signature: TSignature) -> dict[Callable, None]:
        raise NotImplementedError

    def harvest(self, scope: dict, call_value: TCallValue) -> dict[Callable, None]:
        raise NotImplementedError

    def access(self, scope: dict, signature: TSignature) -> dict[Callable, None] | None:
        raise NotImplementedError
