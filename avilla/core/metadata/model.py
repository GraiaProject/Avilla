from __future__ import annotations

from contextvars import ContextVar
from dataclasses import dataclass
from typing import TYPE_CHECKING, Any, Generic, TypeVar, overload
from weakref import WeakKeyDictionary

from typing_extensions import Self, TypeVarTuple, Unpack

if TYPE_CHECKING:
    from avilla.core.relationship import Relationship
    from avilla.core.utilles.selector import Selector

T = TypeVar("T")  # 返回值

_Meta_A = TypeVar("_Meta_A", bound="Metadata")

_Meta_B = TypeVar("_Meta_B", bound="Metadata")

TVT = TypeVarTuple("TVT")



class MetadataMCS(type):
    @overload
    def __rshift__(cls: type[_Meta_A], other: type[_Meta_B]) -> CellOf[_Meta_A, _Meta_B]:
        # sourcery skip: instance-method-first-arg-name
        ...

    @overload
    def __rshift__(cls: type[_Meta_A], other: CellOf[Unpack[TVT]]) -> CellOf[_Meta_A, Unpack[TVT]]:
        # sourcery skip: instance-method-first-arg-name
        ...

    def __rshift__(cls: Any, other: type[Metadata] | CellOf) -> CellOf:
        # sourcery skip: instance-method-first-arg-name
        cells = (cls, other) if isinstance(other, type) else (cls, *other.cells)
        return CellOf(cells)

    @overload
    def __add__(cls: type[_Meta_A], other: type[_M]) -> CellCompose[_Meta_A, _M]:
        # sourcery skip: instance-method-first-arg-name
        ...

    @overload
    def __add__(cls: type[_Meta_A], other: _DeriveBack[_M_k]) -> CellCompose[_Meta_A, _M_k]:
        # sourcery skip: instance-method-first-arg-name
        ...

    @overload
    def __add__(cls: type[_Meta_A], other: CellCompose[Unpack[Ts]]) -> CellCompose[_Meta_A, Unpack[Ts]]:
        # sourcery skip: instance-method-first-arg-name
        ...

    def __add__(cls: Any, other: type[Metadata] | CellOf | CellCompose) -> CellCompose:
        # sourcery skip: instance-method-first-arg-name
        cells: tuple[type[Metadata] | CellOf, ...] = (
            (cls, other) if isinstance(other, (type, CellOf)) else (cls, *other.cells)
        )
        return CellCompose(cells)

    def __repr__(cls) -> str:
        # sourcery skip: instance-method-first-arg-name
        return cls.__name__


METADATA_PARAMS_CTX: WeakKeyDictionary[type[Metadata], ContextVar[dict[str, Any] | None]] = WeakKeyDictionary()

@dataclass
class Metadata(Generic[T], metaclass=MetadataMCS):
    target: Any
    describe: type[Self] | CellOf  # CellCompose 的行为和单次的行为一样.

    @classmethod
    @property
    def _param_ctx(cls):
        return METADATA_PARAMS_CTX[cls]

    def __init_subclass__(cls) -> None:
        METADATA_PARAMS_CTX[cls] = ContextVar(f"$MetadataParam${cls.__module__}::{cls.__qualname__}", default=None)

    def __init__(self, *, target: Any, describe: type[Self] | CellOf) -> None:
        self._target = target
        self._describe = describe

    @classmethod
    def get_default_target(cls, relationship: Relationship) -> Selector | None:
        return relationship.ctx

    @classmethod
    def get_params(cls) -> dict[str, Any]:
        return cls._param_ctx.get() or {}

    @classmethod
    def set_params(cls, params: dict[str, Any]):
        target = cls._param_ctx.get()
        if target is None:
            target = {}
            cls._param_ctx.set(target)
        target.update(params)

    @classmethod
    def clear_params(cls) -> None:
        cls._param_ctx.set(None)

    @classmethod
    def has_params(cls) -> bool:
        return cls._param_ctx.get() is not None


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

    def clear_params(self) -> None:
        for cell in self.cells:
            cell.clear_params()

    def has_params(self) -> bool:
        return any(cell.has_params() for cell in self.cells)


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

    def clear_params(self) -> None:
        for cell in self.cells:
            cell.clear_params()

    def has_params(self) -> bool:
        return any(cell.has_params() for cell in self.cells)
