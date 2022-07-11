from __future__ import annotations

from collections import ChainMap
from itertools import filterfalse
from typing import Any, Callable, Literal, Protocol, runtime_checkable

from typing_extensions import Self

MatchRule = Literal["exact", "exist", "any", "fragment"]
Pattern = str | Callable[[str], bool]


class Selector:
    mode: MatchRule = "exact"
    pattern: dict[str, str]
    path_excludes: frozenset[str]
    referent: Any = None

    def __init__(self, *, mode: MatchRule = "exact", path_excludes: frozenset[str] = frozenset()) -> None:
        self.mode = mode
        self.path_excludes = path_excludes
        self.pattern = {}

    def __getattr__(self, name: str) -> Callable[[str], Self]:
        def wrapper(content: str) -> Self:
            self.pattern[name] = content
            return self

        return wrapper

    def __contains__(self, key: str) -> bool:
        return key in self.pattern

    def __getitem__(self, key: str) -> str:
        return self.pattern[key]

    def __repr__(self) -> str:
        return f"Selector(mode={self.mode}).{'.'.join(f'{k}({v})' for k, v in self.pattern.items())}"

    @property
    def empty(self) -> bool:
        return not self.pattern

    @property
    def path(self) -> str:
        return ".".join(filterfalse(self.path_excludes.__contains__, self.pattern))

    @classmethod
    def exist(cls) -> Self:
        return cls(mode="exist")

    @classmethod
    def any(cls) -> Self:
        return cls(mode="any")

    @classmethod
    def fragment(cls, *path_excludes: str) -> Self:
        return cls(mode="fragment", path_excludes=frozenset(path_excludes))

    def match(self, other: Selector) -> bool:
        try:
            match = {
                "exact": self._match_exact,
                "exist": self._match_exist,
                "any": self._match_any,
                "fragment": self._match_fragment,
            }[self.mode]
        except KeyError:
            raise ValueError(f"Unknown match rule: {self.mode}") from None

        return match(other)

    def _match_exact(self, other: Selector) -> bool:
        if type(other) is Selector:
            return self.path == self.path and self.pattern == other.pattern
        return other._match_exact(self)

    def _match_exist(self, other: Selector) -> bool:
        return set(self.pattern.items()).issubset(other.pattern.items())

    def _match_fragment(self, other: Selector) -> bool:
        fragment = list(self.pattern.items())
        full = list(other.pattern.items())

        try:
            start = full.index(fragment[0])
        except (IndexError, ValueError):  # IndexError有必要吗？自身没有pattern时应该为真（？
            return False

        return full[start : start + len(fragment)] == fragment

    def _match_any(self, other: Selector) -> bool:
        return True

    def mix(self, path: str, **pattern: str) -> Self:
        pattern = self.pattern | pattern
        instance = self.__class__(mode=self.mode, path_excludes=self.path_excludes)

        try:
            instance.pattern = {each: pattern[each] for each in path.split(".")}
        except KeyError:
            raise ValueError(f"given information cannot mix with {path}") from None

        return instance

    def mixin(self, path: str, *selectors: Self) -> Self:
        return self.mix(path, **ChainMap(*(x.pattern for x in selectors)))

    def copy(self) -> Self:
        instance = self.__class__(mode=self.mode, path_excludes=self.path_excludes)
        instance.pattern = self.pattern.copy()
        return instance

    def set_referent(self, referent: Any) -> Self:
        self.referent = referent
        return self


class DynamicSelector(Selector):
    pattern: dict[str, Pattern]

    def __getattr__(self, name: str, /):
        def wrapper(content: Pattern | Literal["*"]):
            if content == "*":
                content = lambda _: True

            self.pattern[name] = content
            return self

        return wrapper

    __getitem__: Callable[[str], Pattern]

    @classmethod
    def way(cls, path: str) -> Selector:
        instance = cls()
        instance.pattern = {i: lambda _: True for i in path.split(".")}
        return instance

    def _match_exact(self, other: Selector) -> bool:
        if isinstance(other, DynamicSelector):
            raise TypeError("Can't match dynamic selector with another dynamic selector")
        return set(other.pattern.items()).issubset(self.pattern.items())

    def _match_exist(self, other: Selector) -> bool:
        for a, b in ((self.pattern[path], other.pattern[path]) for path in self.pattern):
            if callable(a):
                if callable(b):
                    raise TypeError("Can't partially match dynamic selector with another dynamic selector")
                elif not a(b):
                    return False
            elif a != b:
                return False

        return True

    def _match_fragment(self, other: Selector) -> bool:
        fragment = list(self.pattern)
        full = list(other.pattern)

        try:
            start = full.index(fragment[0])
        except (IndexError, ValueError):  # IndexError有必要吗？自身没有pattern时应该为真（？
            return False

        full = full[start : start + len(fragment)]
        if fragment != full:
            return False

        for a, b in ((self.pattern[path], other.pattern[path]) for path in fragment):
            if callable(a):
                if callable(b):
                    raise TypeError("Can't partially match dynamic selector with another dynamic selector")
                elif not a(b):
                    return False
            elif a != b:
                return False

        return True


@runtime_checkable
class Summarizable(Protocol):
    def to_selector(self) -> Selector:
        ...
