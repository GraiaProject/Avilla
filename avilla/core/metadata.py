from __future__ import annotations

from contextvars import ContextVar
from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Any, Generic, TypeVar, Union, overload
from weakref import WeakKeyDictionary

from typing_extensions import Self, TypeVarTuple, Unpack

from avilla.core.utilles import classproperty

T = TypeVar("T")

_MetadataT1 = TypeVar("_MetadataT1", bound="Metadata")
_MetadataT2 = TypeVar("_MetadataT2", bound="Metadata")

_TVT1 = TypeVarTuple("_TVT1")
_TVT2 = TypeVarTuple("_TVT2")


class _GetItemAgent(Generic[T]):
    __getitem__: T

    def __init__(self, getitem: T):
        self.__getitem__ = getitem


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


METACELL_PARAMS_CTX: WeakKeyDictionary[type[Metadata], ContextVar[dict[str, Any] | None]] = WeakKeyDictionary()


@dataclass
class Metadata(metaclass=MetadataMeta):
    route: type[Self] | MetadataRoute = field(init=False)

    def infers(self, route: type[Self] | MetadataRoute):
        self.route = route
        return self

    def __post_init__(self):
        self.route = type(self)

    @classproperty
    @classmethod
    def _param_ctx(cls):
        return METACELL_PARAMS_CTX[cls]

    def __init_subclass__(cls) -> None:
        METACELL_PARAMS_CTX[cls] = ContextVar(f"$MetadataParam${cls.__module__}::{cls.__qualname__}", default=None)
        super().__init_subclass__()

    if TYPE_CHECKING:

        @classmethod
        def inh(cls: type[_MetadataT1]) -> _MetadataT1:
            ...

    else:

        @classmethod
        def inh(cls: type[_MetadataT1]) -> FieldReference[_MetadataT1]:
            return FieldReference(cls)

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

    def clear_params(self) -> None:
        for cell in self.cells:
            cell.clear_params()

    if TYPE_CHECKING:

        @property
        def inh(self: MetadataRoute[Unpack[tuple[Any, ...]], _MetadataT1]) -> _MetadataT1:
            ...

    else:

        @property
        def inh(self: MetadataRoute[Unpack[tuple[Any, ...]], _MetadataT1]) -> RouteFieldReference[_MetadataT1]:
            return RouteFieldReference(self)

    def has_params(self) -> bool:
        return any(cell.has_params() for cell in self.cells)


class FieldReference(Generic[_MetadataT1]):
    def __init__(self, define: type[_MetadataT1]) -> None:
        self.__define = define
        self.__steps: list[str] = []

    def __hash__(self):
        return hash(self.__define) + hash(".".join(self.__steps)) + hash("FieldReference")

    def __eq__(self, other):
        return isinstance(other, FieldReference) and self.__hash__() == other.__hash__()

    def __repr__(self) -> str:
        return f"{self.__define.__name__}.{'.'.join(self.__steps)}"

    def __getattr__(self, item: str) -> Self:
        self.__steps.append(item)
        return self

    def __call__(self, *args: Any, **kwargs: Any) -> Self:
        prev = self.__steps[-1]
        self.__steps[
            -1
        ] = f"{prev}({', '.join(repr(arg) for arg in args)}, {', '.join(f'{key}={repr(value)}' for key, value in kwargs.items())})"
        return self

    def __getitem__(self, item: Any) -> Self:
        prev = self.__steps[-1]
        self.__steps[-1] = f"{prev}[{repr(item)}]"
        return self


class RouteFieldReference(Generic[_MetadataT1]):
    def __init__(self, define: MetadataRoute[Unpack[tuple[Any, ...]], _MetadataT1]) -> None:
        self.__define = define
        self.__steps: list[str] = []

    def __hash__(self):
        return hash(self.__define) + hash(".".join(self.__steps)) + hash("RouteFieldReference")

    def __eq__(self, other):
        return isinstance(other, RouteFieldReference) and self.__hash__() == other.__hash__()

    def __repr__(self) -> str:
        return f"{self.__define.__repr__()}.{'.'.join(self.__steps)}"

    def __getattr__(self, item: str) -> Self:
        self.__steps.append(item)
        return self

    def __call__(self, *args: Any, **kwargs: Any) -> Self:
        prev = self.__steps[-1]
        self.__steps[
            -1
        ] = f"{prev}({', '.join(repr(arg) for arg in args)}, {', '.join(f'{key}={repr(value)}' for key, value in kwargs.items())})"
        return self

    def __getitem__(self, item: Any) -> Self:
        prev = self.__steps[-1]
        self.__steps[-1] = f"{prev}[{repr(item)}]"
        return self


Route = Union[type[Metadata], MetadataRoute]
