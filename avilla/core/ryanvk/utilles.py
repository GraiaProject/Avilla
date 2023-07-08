from __future__ import annotations

from typing import Callable, Generic, overload

from typing_extensions import Concatenate, ParamSpec, Self, TypeVar, Any

P = ParamSpec("P")
R = TypeVar("R", covariant=True)
T = TypeVar("T")
Q = TypeVar("Q", contravariant=True)


class doubledself(Generic[Q, P, R]):
    """和普通的方法差不多, 唯一的差别就是 self 会传两个, (self0, self1, ...), 用于制服 pyright.
    有一个问题, 就是强行 apply 上原方法会寄. 我需要一种能自动取两个 var 并集的 type operator 方法,
    或者我就只能 type: ignore
    """

    def __init__(self, fn: Callable[Concatenate[Q, Q, P], R]):
        self.fn = fn

    @overload
    def __get__(self, instance: None, owner: type[Q]) -> Self:
        ...

    @overload
    def __get__(self, instance: Any, owner: type[Q]) -> Callable[P, R]:
        ...

    def __get__(self, instance: Q | None, owner: type[Q]):
        if instance is None:
            return self

        def wrapper(*args: P.args, **kwargs: P.kwargs) -> R:
            return self.fn(instance, instance, *args, **kwargs)

        return wrapper


class doubledself_property(Generic[Q, R]):
    """和普通的方法差不多, 唯一的差别就是 self 会传两个, (self0, self1, ...), 用于制服 pyright.
    有一个问题, 就是强行 apply 上原方法会寄. 我需要一种能自动取两个 var 并集的 type operator 方法,
    或者我就只能 type: ignore
    """

    def __init__(self, fn: Callable[[Q, Q], R]):
        self.fn = fn

    @overload
    def __get__(self, instance: None, owner: type[Q]) -> Self:
        ...

    @overload
    def __get__(self, instance: Any, owner: type[Q]) -> R:
        ...

    def __get__(self, instance: Q | None, owner: type[Q]):
        if instance is None:
            return self

        return self.fn(instance, instance)
