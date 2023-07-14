from __future__ import annotations

from typing import Callable, Protocol, TypeVar

from typing_extensions import ParamSpec

P = ParamSpec("P")
R = TypeVar("R", covariant=True)


class K(Protocol[P, R]):
    def __call__(self, *args: P.args, **kwargs: P.kwargs) -> R:
        ...

def x(a: K[P, R], *args: P.args, **kwargs: P.kwargs) -> R:
    ...


T = TypeVar("T")

class X:
    @classmethod
    def __call__(cls, n: type[T]):
        def receiver(entity: Callable[[T], int]):
            return entity
        return receiver

reveal_type(x(X(), int)(lambda x: x)(63456))


def p(m: dict[{"a": K[P, R]}]):
    return m["a"]

reveal_type(p({"a": x}))