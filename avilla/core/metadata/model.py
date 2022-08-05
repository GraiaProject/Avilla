from __future__ import annotations

import inspect
from abc import ABCMeta, abstractmethod
from dataclasses import dataclass
from typing import TYPE_CHECKING, Any, Generic, TypeVar, overload

from typing_extensions import Self, TypeVarTuple, Unpack

if TYPE_CHECKING:
    from avilla.core.metadata.source import MetadataSource
    from avilla.core.relationship import Relationship
    from avilla.core.utilles.selector import Selector

T = TypeVar("T")  # 返回值


@dataclass
class MetadataModifies(Generic[T]):
    target: Any
    model: type[Metadata]
    modified: list[str]
    past: dict[str, Any]
    current: dict[str, Any]


M = TypeVar("M", bound=MetadataModifies)


class MetaField:
    id: str

    def __init__(self, id: str) -> None:
        self.id = id

    def __get__(self, instance: Metadata | None, owner: type[Metadata]) -> Any:
        # sourcery skip: assign-if-exp, reintroduce-else
        if instance is None:
            return self
        return instance._content[self.id]

    def __set__(self, instance: Metadata, value: Any) -> None:
        modifies = instance._modifies
        if modifies is None:
            modifies = MetadataModifies(instance, instance.__class__, [], {}, {})
        modifies.modified.append(self.id)
        modifies.past[self.id] = instance._content[self.id]
        modifies.current[self.id] = value
        instance._content[self.id] = value


def meta_field(id: str) -> Any:
    return MetaField(id)


_Meta_A = TypeVar("_Meta_A", bound="Metadata")

_Meta_B = TypeVar("_Meta_B", bound="Metadata")


TVT = TypeVarTuple("TVT")

# TODO: add params


class MetadataMCS(type):
    @overload
    def __rshift__(cls: type[_Meta_A], other: type[_Meta_B]) -> CellOf[_Meta_A, _Meta_B]:
        ...

    @overload
    def __rshift__(cls: type[_Meta_A], other: CellOf[Unpack[TVT]]) -> CellOf[_Meta_A, Unpack[TVT]]:
        ...

    def __rshift__(cls: Any, other: type[Metadata] | CellOf) -> CellOf:
        cells = (cls, other) if isinstance(other, type) else (cls, *other.cells)
        return CellOf(cells)

    @overload
    def __add__(cls: type[_Meta_A], other: type[_M]) -> CellCompose[_Meta_A, _M]:
        ...

    @overload
    def __add__(cls: type[_Meta_A], other: _DeriveBack[_M_k]) -> CellCompose[_Meta_A, _M_k]:
        ...

    @overload
    def __add__(cls: type[_Meta_A], other: CellCompose[Unpack[Ts]]) -> CellCompose[_Meta_A, Unpack[Ts]]:
        ...

    def __add__(cls: Any, other: type[Metadata] | CellOf | CellCompose) -> CellCompose:
        cells: tuple[type[Metadata] | CellOf, ...] = (
            (cls, other) if isinstance(other, (type, CellOf)) else (cls, *other.cells)
        )
        return CellCompose(cells)

    def __repr__(cls) -> str:
        return cls.__name__


class Metadata(Generic[T], metaclass=MetadataMCS):
    _target: Any
    _source: MetadataSource
    _content: dict[str, Any]
    _modifies: MetadataModifies[T] | None = None

    def __init__(self, *, target: Any, source: MetadataSource, content: dict[str, Any] | None = None) -> None:
        self._target = target
        self._source = source
        self._content = content or {}

    def modifies(self) -> MetadataModifies[T] | None:
        return self._modifies

    @classmethod
    def fields(cls) -> list[MetaField]:
        return [v for _, v in inspect.getmembers(cls, lambda x: isinstance(x, MetaField))]

    def __repr__(self) -> str:
        values = ", ".join(f"{k}={repr(v)}" for k, v in self._content.items() if not k.startswith("_"))
        return f"{self.__class__.__name__}({values})"

    @classmethod
    def get_default_target(cls, relationship: Relationship) -> Selector | None:
        return relationship.ctx


Ts = TypeVarTuple("Ts")

_M = TypeVar("_M", bound=Metadata)

_M_k = TypeVar("_M_k", bound=Metadata)


class CellOf(Generic[Unpack[TVT]]):
    cells: tuple[type[Metadata], ...]

    def __init__(self, cells: tuple[type[Metadata], ...]) -> None:
        self.cells = cells

    def get_default_target(self, relationship: Relationship) -> Selector | None:
        return self.cells[0].get_default_target(relationship)

    @overload
    def __rshift__(self: CellOf[Unpack[TVT]], other: type[_M]) -> CellOf[Unpack[TVT], _M]:
        ...

    @overload
    def __rshift__(self: CellOf[Unpack[TVT]], other: CellOf[Unpack[Ts]]) -> CellOf[Unpack[TVT], Unpack[Ts]]:
        ...

    def __rshift__(self, other: type[Metadata] | CellOf) -> CellOf:
        if not isinstance(other, (type, CellOf)):
            raise TypeError(f"{other.__class__} is not allowed.")
        cells = (*self.cells, other) if isinstance(other, type) else (*self.cells, *other.cells)
        return CellOf(cells)

    @overload
    def __add__(self: _DeriveBack[_M_k], other: type[_M]) -> CellCompose[_M_k, _M]:
        ...

    @overload
    def __add__(self: _DeriveBack[_M_k], other: _DeriveBack[_M]) -> CellCompose[_M_k, _M]:
        ...

    @overload
    def __add__(self: _DeriveBack[_M_k], other: CellCompose[Unpack[Ts]]) -> CellCompose[_M_k, Unpack[Ts]]:
        ...

    def __add__(self, other: type[Metadata] | CellOf | CellCompose) -> CellCompose:
        cells: tuple[type[Metadata] | CellOf, ...] = (
            (self, other) if isinstance(other, (type, CellOf)) else (self, *other.cells)
        )
        return CellCompose(cells)

    def __repr__(self) -> str:
        cells_repr = ", ".join(repr(cell) for cell in self.cells)
        return f"CellOf[{cells_repr}]"

    def __hash__(self) -> int:
        return hash(self.cells) + hash("CellOf")

    def __eq__(self, o: object) -> bool:
        return isinstance(o, CellOf) and o.cells == self.cells


_DeriveBack = CellOf[Unpack[tuple[Any, ...]], _M_k]


class CellCompose(Generic[Unpack[TVT]]):
    cells: tuple[type[Metadata] | CellOf, ...]

    def __init__(self, cells: tuple[type[Metadata] | CellOf, ...]) -> None:
        self.cells = cells

    @overload
    def __add__(self, other: type[_M]) -> CellCompose[Unpack[TVT], _M]:
        ...

    @overload
    def __add__(self, other: _DeriveBack[_M]) -> CellCompose[Unpack[TVT], _M]:
        ...

    @overload
    def __add__(self, other: CellCompose[Unpack[Ts]]) -> CellCompose[Unpack[TVT], Unpack[Ts]]:
        ...

    def __add__(self, other: type[Metadata] | CellOf | CellCompose) -> CellCompose:
        cells: tuple[type[Metadata] | CellOf, ...] = (
            (*self.cells, other) if isinstance(other, (type, CellOf)) else (*self.cells, *other.cells)
        )
        return CellCompose(cells)

    def get_default_target(self, relationship: Relationship) -> Selector | None:
        return self.cells[0].get_default_target(relationship)

    def __repr__(self) -> str:
        cells_repr = ", ".join(repr(cell) for cell in self.cells)
        return f"CellCompose[{cells_repr}]"

    def __hash__(self) -> int:
        return hash(self.cells) + hash("CellCompose")

    def __eq__(self, o: object) -> bool:
        return isinstance(o, CellCompose) and o.cells == self.cells
