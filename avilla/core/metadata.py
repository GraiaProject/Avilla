from __future__ import annotations

from contextvars import ContextVar
from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Any, Callable, Generic, TypeVar, overload
from weakref import WeakKeyDictionary

from typing_extensions import Self, TypeVarTuple, Unpack

from avilla.core.utilles import classproperty

if TYPE_CHECKING:
    from avilla.core.context import Context
    from avilla.core.selector import Selector

T = TypeVar("T")

_MetadataT1 = TypeVar("_MetadataT1", bound="Metadata")
_MetadataT2 = TypeVar("_MetadataT2", bound="Metadata")

_DescribeT = TypeVar("_DescribeT", bound="type[Metadata] | MetadataRoute")

_TVT1 = TypeVarTuple("_TVT1")
_TVT2 = TypeVarTuple("_TVT2")


@dataclass
class MetadataOf(Generic[_DescribeT]):
    target: Selector
    describe: _DescribeT

    def to_bounding(self):
        return MetadataBound(self.target.path_without_land, self.describe)


@dataclass
class MetadataBound(Generic[_DescribeT]):
    target: str
    describe: _DescribeT


class _SetItemAgent:
    def __init__(self, setitem):
        self.__setitem__ = setitem


class MetadataMeta(type):
    @overload
    def __rshift__(cls: type[_MetadataT1], other: type[_MetadataT2]) -> MetadataRoute[_MetadataT1, _MetadataT2]:
        ...

    @overload
    def __rshift__(
        cls: type[_MetadataT1], other: MetadataRoute[Unpack[_TVT1]]
    ) -> MetadataRoute[_MetadataT1, Unpack[_TVT1]]:
        ...

    def __rshift__(cls: Any, other: type[Metadata] | MetadataRoute) -> MetadataRoute:
        # sourcery skip: instance-method-first-arg-name
        cells = (cls, other) if isinstance(other, type) else (cls, *other.cells)
        return MetadataRoute(cells)

    """
    def __repr__(cls) -> str:
        # sourcery skip: instance-method-first-arg-name
        return cls.__name__
    """


METACELL_PARAMS_CTX: WeakKeyDictionary[type[Metadata], ContextVar[dict[str, Any] | None]] = WeakKeyDictionary()


@dataclass
class Metadata(metaclass=MetadataMeta):
    route: type[Self] | MetadataRoute = field(init=False)

    def infers(self, route: type[Self] | MetadataRoute):
        self.route = route
        return self

    def __post_init__(self):
        self.route = type(self)

    @classmethod
    def of(cls, target: Selector) -> MetadataOf[type[Self]]:
        return MetadataOf(target, cls)

    @classproperty
    @classmethod
    def _param_ctx(cls):
        return METACELL_PARAMS_CTX[cls]

    def __init_subclass__(cls) -> None:
        METACELL_PARAMS_CTX[cls] = ContextVar(f"$MetadataParam${cls.__module__}::{cls.__qualname__}", default=None)

    @classproperty
    @classmethod
    def _(cls):
        @_SetItemAgent
        def wrapper(operator: Callable[[Self], T]) -> MetadataFieldReference[Self, T]:
            return MetadataFieldReference(cls, operator)

        return wrapper

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


class MetadataRoute(Generic[Unpack[_TVT1]]):
    cells: tuple[type[Metadata], ...]

    def __init__(self, cells: tuple[type[Metadata], ...]) -> None:
        self.cells = cells

    @overload
    def __rshift__(
        self: MetadataRoute[Unpack[_TVT1]], other: type[_MetadataT1]
    ) -> MetadataRoute[Unpack[_TVT1], _MetadataT1]:
        ...

    @overload
    def __rshift__(
        self: MetadataRoute[Unpack[_TVT1]], other: MetadataRoute[Unpack[_TVT2]]
    ) -> MetadataRoute[Unpack[_TVT1], Unpack[_TVT2]]:
        ...

    def __rshift__(self, other: type[Metadata] | MetadataRoute) -> MetadataRoute:
        if not isinstance(other, (type, MetadataRoute)):
            raise TypeError(f"{other.__class__} is not allowed.")
        cells = (*self.cells, other) if isinstance(other, type) else (*self.cells, *other.cells)
        return MetadataRoute(cells)

    def __repr__(self) -> str:
        cells_repr = " >> ".join(cell.__name__ for cell in self.cells)
        return f"MetadataRoute[{cells_repr}]"

    def __hash__(self) -> int:
        return hash(self.cells) + hash("MetadataRoute")

    def __eq__(self, o: object) -> bool:
        return isinstance(o, MetadataRoute) and o.cells == self.cells

    def of(self, target: Selector) -> MetadataOf[Self]:
        return MetadataOf(target, self)

    def clear_params(self) -> None:
        for cell in self.cells:
            cell.clear_params()

    @property
    def _(self: MetadataRoute[Unpack[tuple[Any, ...]], _MetadataT1]):
        @_SetItemAgent
        def wrapper(operator: Callable[[_MetadataT1], T]) -> MetadataFieldReference[_MetadataT1, T]:
            return MetadataFieldReference(self, operator)

        return wrapper

    def has_params(self) -> bool:
        return any(cell.has_params() for cell in self.cells)


@dataclass
class MetadataFieldReference(Generic[_MetadataT1, T]):
    define: type[_MetadataT1] | MetadataRoute[Unpack[tuple[Any, ...]], _MetadataT1]
    operator: Callable[[_MetadataT1], T]

    def __hash__(self):
        return ("field-ref", self.define, self.operator.__name__, self.operator.__code__)
