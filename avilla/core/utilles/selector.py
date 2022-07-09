from __future__ import annotations

from collections import ChainMap
from typing import (
    Any,
    Callable,
    Generic,
    Literal,
    Protocol,
    TypeVar,
    Union,
    cast,
    runtime_checkable,
)

MatchRule = Literal["exact", "exist", "any"]
Pattern = Union[str, Callable[[str], bool]]

P = TypeVar("P", bound=str)


class Selector(Generic[P]):
    match_rule: MatchRule = "exact"

    pattern: dict[str, Pattern]
    path_excludes: tuple[str]

    def __init__(self, *, match_rule: MatchRule = "exact", path_excludes: tuple[str, ...] = ()):
        self.match_rule = match_rule
        self.path_excludes = path_excludes
        self.pattern = {}

    def __getattr__(self, name: str):
        def wrapper(content: Pattern):
            self.pattern[name] = content
            return self

        return wrapper

    def contains(self, key: str) -> bool:
        return key in self.pattern

    __contains__ = contains

    def __getitem__(self, key: str) -> Pattern:
        return self.pattern[key]

    @property
    def constant(self) -> bool:
        return all(not callable(v) for v in self.pattern.values())

    @property
    def path(self) -> P | str:
        return ".".join(k for k in self.pattern.keys() if k not in self.path_excludes)

    def match(self, another: Selector) -> bool:
        if self.match_rule == "exact":
            if self.constant:
                return another.constant and self.path == another.path and self.pattern == another.pattern
            if not another.constant:
                raise TypeError("Can't match dynamic selector with another dynamic selector")
            return self.path == another.path and all(
                v(cast(str, another.pattern[k])) if callable(v) else v == another.pattern[k]
                for k, v in self.pattern.items()
            )
        elif self.match_rule == "exist":
            subset = set(self.pattern.keys()).issubset(another.pattern.keys())
            if self.constant:
                return subset and all(v == another.pattern[k] for k, v in self.pattern.items() if k in another.pattern)
            if not another.constant and any(callable(v) for k, v in another.pattern.items() if k in self.pattern):
                raise TypeError("Can't partially match dynamic selector with another dynamic selector")
            return subset and all(
                v(cast(str, another.pattern[k])) if callable(v) else v == another.pattern[k]
                for k, v in self.pattern.items()
                if k in another.pattern
            )
        elif self.match_rule == "any":
            return True
        else:
            raise ValueError(f"Unknown match rule: {self.match_rule}")

    def mix(self, path: str, **env: Pattern) -> Selector:
        env.update(self.pattern)
        instance = super().__new__(self.__class__)
        instance.match_rule = self.match_rule
        if not set(env).issuperset(path.split(".")):
            raise ValueError(f"given information cannot mix with {path}")
        instance.pattern = {each: env[each] for each in path.split(".")}
        return instance

    def mixin(self, path: str, *selectors: Selector) -> Selector:
        return self.mix(path, **ChainMap(*(x.pattern for x in selectors)))

    def copy(self) -> Selector:
        instance = super().__new__(self.__class__)
        instance.match_rule = self.match_rule
        instance.pattern = self.pattern.copy()
        return instance

    referent: Any = None

    def set_referent(self, referent: Any):
        self.referent = referent
        return self


@runtime_checkable
class Summarizable(Protocol):
    def to_selector(self) -> Selector:
        ...
