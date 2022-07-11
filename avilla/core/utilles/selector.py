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
    runtime_checkable,
)

from typing_extensions import LiteralString

MatchRule = Literal["exact", "exist", "any", "fragment"]
Pattern = Union[str, Callable[[str], bool]]

P = TypeVar("P", bound=str)
TLiteral = TypeVar("TLiteral", bound=LiteralString)


class Selector(Generic[P]):
    match_rule: MatchRule = "exact"

    pattern: dict[str, Pattern]
    path_excludes: tuple[str]

    def __init__(self, *, match_rule: MatchRule = "exact", path_excludes: tuple[str, ...] = ()):
        self.match_rule = match_rule
        self.path_excludes = path_excludes
        self.pattern = {}

    def __getattr__(self, name: str):
        def wrapper(content: Pattern | Literal["*"]):
            if content == "*":
                content = lambda _: True
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
    def empty(self) -> bool:
        return not self.pattern

    @property
    def path(self) -> P | str:
        return ".".join(k for k in self.pattern.keys() if k not in self.path_excludes)

    @classmethod
    def exist(cls):
        return cls(match_rule="exist")

    @classmethod
    def any(cls):
        return cls(match_rule="any")

    @classmethod
    def way(cls, path: TLiteral) -> Selector[TLiteral]:
        instance = cls()
        instance.pattern = {i: lambda _: True for i in path.split(".")}
        return instance  # type: ignore

    def match(self, another: Selector) -> bool:
        # sourcery skip: low-code-quality
        if self.match_rule == "exact":
            if self.constant:
                return another.constant and self.path == another.path and self.pattern == another.pattern
            if not another.constant:
                raise TypeError("Can't match dynamic selector with another dynamic selector")
            for k, v1 in self.pattern.items():
                v2 = another.pattern[k]
                if v1 != v2:
                    return False
            return True
        elif self.match_rule == "exist":
            subset = set(self.pattern.keys()).issubset(another.pattern.keys())
            if not subset:
                return False
            if not another.constant and any(callable(v) for k, v in another.pattern.items() if k in self.pattern):
                raise TypeError("Can't partially match dynamic selector with another dynamic selector")
            for k, v1 in self.pattern.items():
                if k in another.pattern:
                    v2 = another.pattern[k]
                    if callable(v1):
                        if callable(v2):
                            raise TypeError("Can't partially match dynamic selector with another dynamic selector")
                        if not v1(v2):
                            return False
                    elif v1 != v2:
                        return False
            return True
        elif self.match_rule == "fragment":
            if self.empty:
                return True
            fragment = list(self.pattern.keys())
            full = list(another.pattern.keys())
            try:
                start = full.index(fragment[0])
            except IndexError:
                return False
            sub = full[start:start+len(fragment)]
            if len(sub) != len(fragment):
                return False
            for k1, k2 in zip(fragment, sub):
                if k1 != k2:
                    return False
                v1 = self.pattern[k1]
                v2 = another.pattern[k2]
                if callable(v1):
                    if callable(v2):
                        raise TypeError("Can't partially match dynamic selector with another dynamic selector")
                    if not v1(v2):
                        return False
                elif v1 != v2:
                    return False
            return True
        elif self.match_rule == "any":
            return True
        else:
            raise ValueError(f"Unknown match rule: {self.match_rule}")

    def mix(self, path: str, **env: Pattern) -> Selector:
        env = self.pattern.copy() | env
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
