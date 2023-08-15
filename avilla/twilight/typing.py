"""Ariadne 的类型标注"""


import contextlib
import enum
import sys
import types
from types import TracebackType
from typing import (
    TYPE_CHECKING,
    AbstractSet,
    Any,
    Callable,
    Dict,
    Final,
    Generic,
    Literal,
    Mapping,
    Optional,
    Sequence,
    Tuple,
    Type,
    TypeVar,
    Union,
)

import typing_extensions
from typing_extensions import Annotated, ParamSpec, TypeAlias, get_args

P = ParamSpec("P")
R = TypeVar("R")
T = TypeVar("T")
T_co = TypeVar("T_co", covariant=True)

T_start = TypeVar("T_start")
T_stop = TypeVar("T_stop")
T_step = TypeVar("T_step")


MessageIndex: TypeAlias = Union[Tuple[int, Optional[int]], int]

IntStr: TypeAlias = Union[int, str]
AbstractSetIntStr: TypeAlias = AbstractSet[IntStr]
DictIntStrAny: TypeAlias = Dict[IntStr, Any]
DictStrAny: TypeAlias = Dict[str, Any]
MappingIntStrAny: TypeAlias = Mapping[IntStr, Any]
ReprArgs: TypeAlias = Sequence[Tuple[Optional[str], Any]]
Unions: Tuple[Any, ...] = (Union, types.UnionType) if sys.version_info >= (3, 10) else (Union,)


def generic_issubclass(cls: Any, par: Union[type, Any, Tuple[type, ...]]) -> bool:
    """检查 cls 是否是 args 中的一个子类, 支持泛型, Any, Union

    Args:
        cls (type): 要检查的类
        par (Union[type, Any, Tuple[type, ...]]): 要检查的类的父类

    Returns:
        bool: 是否是父类
    """
    if par is Any:
        return True
    with contextlib.suppress(TypeError):
        if isinstance(par, AnnotatedType):
            return generic_issubclass(cls, get_args(par)[0])
        if isinstance(par, (type, tuple)):
            return issubclass(cls, par)
        if get_origin(par) in Unions:
            return any(generic_issubclass(cls, p) for p in get_args(par))
        if isinstance(par, TypeVar):
            if par.__constraints__:
                return any(generic_issubclass(cls, p) for p in par.__constraints__)
            if par.__bound__:
                return generic_issubclass(cls, par.__bound__)
    return False


def get_origin(obj: Any) -> Any:
    return typing_extensions.get_origin(obj) or obj


def generic_isinstance(obj: Any, par: Union[type, Any, Tuple[type, ...]]) -> bool:
    """检查 obj 是否是 args 中的一个类型, 支持泛型, Any, Union

    Args:
        obj (Any): 要检查的对象
        par (Union[type, Any, Tuple[type, ...]]): 要检查的对象的类型

    Returns:
        bool: 是否是类型
    """
    if par is Any:
        return True
    with contextlib.suppress(TypeError):
        if isinstance(par, AnnotatedType):
            return generic_isinstance(obj, get_args(par)[0])
        if isinstance(par, (type, tuple)):
            return isinstance(obj, par)
        if get_origin(par) in Unions:
            return any(generic_isinstance(obj, p) for p in get_args(par))
        if isinstance(par, TypeVar):
            if par.__constraints__:
                return any(generic_isinstance(obj, p) for p in par.__constraints__)
            if par.__bound__:
                return generic_isinstance(obj, par.__bound__)
    return False


class _SentinelClass(enum.Enum):
    _Sentinel = object()


Sentinel: Final = _SentinelClass._Sentinel

FlagAlias: TypeAlias = Literal[Sentinel]
MaybeFlag: TypeAlias = Union[Literal[Sentinel], T]

T_Callable = TypeVar("T_Callable", bound=Callable)

Wrapper: TypeAlias = Callable[[T_Callable], T_Callable]

if TYPE_CHECKING:
    AnnotatedType = type
else:
    AnnotatedType = type(Annotated[int, lambda x: x > 0])

ExceptionHook: TypeAlias = Callable[[Type[BaseException], BaseException, Optional[TracebackType]], Any]


class class_property(Generic[T]):
    """Class-level property.
    Link: https://stackoverflow.com/a/13624858/1280629
    """

    def __init__(self, fget: Callable[[Any], T]):
        self.fget = fget

    def __get__(self, _, owner_cls) -> T:
        return self.fget(owner_cls)
