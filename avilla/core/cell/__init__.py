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

_Meta_A = TypeVar("_Meta_A", bound="Cell")

_Meta_B = TypeVar("_Meta_B", bound="Cell")

TVT = TypeVarTuple("TVT")


class CellMeta(type):
    @overload
    def __rshift__(cls: type[_Meta_A], other: type[_Meta_B]) -> CellOf[_Meta_A, _Meta_B]:
        # sourcery skip: instance-method-first-arg-name
        ...

    @overload
    def __rshift__(cls: type[_Meta_A], other: CellOf[Unpack[TVT]]) -> CellOf[_Meta_A, Unpack[TVT]]:
        # sourcery skip: instance-method-first-arg-name
        ...

    def __rshift__(cls: Any, other: type[Cell] | CellOf) -> CellOf:
        # sourcery skip: instance-method-first-arg-name
        cells = (cls, other) if isinstance(other, type) else (cls, *other.cells)
        return CellOf(cells)

    def __repr__(cls) -> str:
        # sourcery skip: instance-method-first-arg-name
        return cls.__name__


METACELL_PARAMS_CTX: WeakKeyDictionary[type[Cell], ContextVar[dict[str, Any] | None]] = WeakKeyDictionary()


@dataclass
class Cell(Generic[T], metaclass=CellMeta):
    describe: type[Self] | CellOf  # CellCompose 的行为和单次的行为一样.

    @classmethod
    @property
    def _param_ctx(cls):
        return METACELL_PARAMS_CTX[cls]

    def __init_subclass__(cls) -> None:
        METACELL_PARAMS_CTX[cls] = ContextVar(f"$MetadataParam${cls.__module__}::{cls.__qualname__}", default=None)

    @classmethod
    def get_default_target(cls, relationship: Relationship) -> Selector | None:
        return relationship.ctx.to_selector()

    @classmethod
    def get_params(cls) -> dict[str, Any] | None:
        return cls._param_ctx.get()

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

_M = TypeVar("_M", bound=Cell)

_M_k = TypeVar("_M_k", bound=Cell)


class CellOf(Generic[Unpack[TVT]]):
    cells: tuple[type[Cell], ...]

    def __init__(self, cells: tuple[type[Cell], ...]) -> None:
        self.cells = cells

    def get_default_target(self, relationship: Relationship) -> Selector | None:
        return self.cells[0].get_default_target(relationship)

    @overload
    def __rshift__(self: CellOf[Unpack[TVT]], other: type[_M]) -> CellOf[Unpack[TVT], _M]:
        ...

    @overload
    def __rshift__(self: CellOf[Unpack[TVT]], other: CellOf[Unpack[Ts]]) -> CellOf[Unpack[TVT], Unpack[Ts]]:
        ...

    def __rshift__(self, other: type[Cell] | CellOf) -> CellOf:
        if not isinstance(other, (type, CellOf)):
            raise TypeError(f"{other.__class__} is not allowed.")
        cells = (*self.cells, other) if isinstance(other, type) else (*self.cells, *other.cells)
        return CellOf(cells)

    def __repr__(self) -> str:
        cells_repr = " >> ".join(cell.__name__ for cell in self.cells)
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
