from __future__ import annotations

from collections import ChainMap
from itertools import filterfalse
from typing import TYPE_CHECKING, Any, Callable, Literal, Protocol, runtime_checkable

from typing_extensions import Self

from avilla.core.platform import Land

if TYPE_CHECKING:
    ...

MatchRule = Literal["any", "exact", "exist", "fragment", "startswith"]
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

    def __hash__(self) -> int:
        return hash("Selector") + hash(tuple(self.pattern.items()))

    def __eq__(self, o: object) -> bool:
        return isinstance(o, Selector) and o.pattern == self.pattern

    def __contains__(self, key: str) -> bool:
        return key in self.pattern

    def __getitem__(self, key: str) -> str:
        return self.pattern[key]

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(mode={self.mode}).{'.'.join(f'{k}({v})' for k, v in self.pattern.items())}"

    @property
    def empty(self) -> bool:
        return not self.pattern

    @property
    def path(self) -> str:
        return ".".join(filterfalse(self.path_excludes.__contains__, self.pattern))

    @property
    def path_without_land(self) -> str:
        return ".".join(filterfalse((self.path_excludes | {"land"}).__contains__, self.pattern))

    @classmethod
    def exist(cls) -> Self:
        return cls(mode="exist")

    @classmethod
    def any(cls) -> Self:
        return cls(mode="any")

    @classmethod
    def fragment(cls, *path_excludes: str) -> Self:
        return cls(mode="fragment", path_excludes=frozenset(path_excludes))

    @classmethod
    def from_dict(cls, pattern: dict) -> Self:
        instance = cls()
        instance.pattern = pattern
        return instance

    @property
    def latest_key(self) -> str:
        return list(self.pattern.keys())[-1]

    def land(self, land: Land | str):
        if isinstance(land, Land):
            land = land.name
        self.pattern["land"] = land
        return self

    def match(self, other: Selector) -> bool:
        if not isinstance(other, Selector):
            return False
        try:
            match = {
                "any": self._match_any,
                "exact": self._match_exact,
                "exist": self._match_exist,
                "fragment": self._match_fragment,
                "startswith": self._match_startswith,
            }[self.mode]
        except KeyError:
            raise ValueError(f"Unknown match rule: {self.mode}") from None

        return match(other)

    def _match_any(self, other: Selector) -> bool:
        return True

    def _match_exact(self, other: Selector) -> bool:
        return type(other) is Selector and self.path == self.path and self.pattern == other.pattern

    def _match_exist(self, other: Selector) -> bool:
        return set(self.pattern.items()).issubset(other.pattern.items())

    def _match_fragment(self, other: Selector) -> bool:
        fragment = list(self.pattern.items())
        full = list(other.pattern.items())

        try:
            start = full.index(fragment[0])
        except IndexError:
            return True
        except ValueError:
            return False

        return full[start : start + len(fragment)] == fragment

    def _match_startswith(self, other: Selector) -> bool:
        fragment = list(self.pattern.items())
        full = list(other.pattern.items())

        return all(fragment[i] == full[i] for i in range(len(fragment)))

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

    def appendix(self, key: str, value: str) -> Self:
        self.pattern[key] = value
        return self

    def copy(self) -> Self:
        instance = self.__class__(mode=self.mode, path_excludes=self.path_excludes)
        instance.pattern = self.pattern.copy()
        return instance

    def as_dyn(self) -> DynamicSelector:
        instance = DynamicSelector(mode=self.mode, path_excludes=self.path_excludes)
        for k, v in self.pattern.items():
            getattr(instance, k)(v)
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

    def __hash__(self) -> int:
        raise TypeError("Dynamic Selector is unhashable.")

    __getitem__: Callable[[str], Pattern]

    @classmethod
    def way(cls, path: str) -> Selector:
        instance = cls()
        instance.pattern = {i: lambda _: True for i in path.split(".")}
        return instance

    def _match_exact(self, other: Selector) -> bool:
        if isinstance(other, DynamicSelector):
            raise TypeError("Can't match dynamic selector with another dynamic selector")
        for k in other.pattern:
            if k not in self.pattern:
                return False
            own_pattern = self.pattern[k]
            if (
                callable(own_pattern)
                and not own_pattern(other.pattern[k])
                or not callable(own_pattern)
                and own_pattern != other.pattern[k]
            ):
                return False
        return True

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
        except IndexError:
            return True
        except ValueError:
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

    def _match_startswith(self, other: Selector) -> bool:
        if not other.path.startswith(self.path):
            return False

        for a, b in ((self.pattern[path], other.pattern[path]) for path in self.pattern):
            if callable(a):
                if callable(b):
                    raise TypeError("Can't partially match dynamic selector with another dynamic selector")
                elif not a(b):
                    return False
            elif a != b:
                return False

        return True


@runtime_checkable
class Selectable(Protocol):
    def to_selector(self) -> Selector:
        ...
