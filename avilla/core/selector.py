from __future__ import annotations

from collections.abc import Callable, Mapping
from itertools import filterfalse
from types import MappingProxyType
from typing import TYPE_CHECKING, Literal, Protocol, Union, runtime_checkable

from typing_extensions import Self

from avilla.core._runtime import ctx_context
from avilla.core.platform import Land

if TYPE_CHECKING:
    from .context import ContextSelector

MatchRule = Literal["any", "exact", "exist", "fragment", "startswith"]
Pattern = Union[str, Callable[[str], bool]]
EMPTY_MAP = MappingProxyType({})


class Selector:
    pattern: Mapping[str, str]

    def __init__(self, pattern: Mapping[str, str] = EMPTY_MAP) -> None:
        self.pattern = MappingProxyType({**pattern})

    def __getattr__(self, name: str) -> Callable[[str], Self]:
        def wrapper(content: str) -> Self:
            return Selector(pattern={**self.pattern, name: content})

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
        return f"{self.__class__.__name__}().{'.'.join(f'{k}({v})' for k, v in self.pattern.items())}"

    @property
    def empty(self) -> bool:
        return not self.pattern

    @property
    def path(self) -> str:
        return ".".join(self.pattern)

    @property
    def path_without_land(self) -> str:
        return ".".join(filterfalse(lambda x: x == "land", self.pattern))

    @property
    def last_key(self) -> str:
        return next(reversed(self.pattern.keys()))

    @property
    def last_value(self) -> str:
        return next(reversed(self.pattern.values()))

    def appendix(self, key: str, value: str):
        return Selector(pattern={**self.pattern, key: value})

    def land(self, land: Land | str):
        if isinstance(land, Land):
            land = land.name

        return Selector({"land": land, **self.pattern})

    def matches(self, other: Selectable, *, mode: MatchRule = "exact") -> bool:
        if not isinstance(other, Selector):
            other = other.to_selector()
        try:
            match = {
                "any": self._match_any,
                "exact": self._match_exact,
                "exist": self._match_exist,
                "fragment": self._match_fragment,
                "startswith": self._match_startswith,
            }[mode]
        except KeyError:
            raise ValueError(f"Unknown match rule: {mode}") from None

        return match(other)

    def _match_any(self, other: Selector) -> bool:
        return True

    def _match_exact(self, other: Selector) -> bool:
        return type(other) is Selector and self.path == other.path and self.pattern == other.pattern

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

    def as_dyn(self) -> DynamicSelector:
        return DynamicSelector(self.pattern)

    def to_selector(self):
        return self

    def follows(self, pattern: str) -> bool:
        patterns: dict[str, str] = {}
        bracket_depth: int = 0
        path_buf: list[str] = []
        pattern_buf: list[str] = []
        for ch in pattern:
            if ch == "." and bracket_depth == 0:
                patterns["".join(path_buf)] = "".join(pattern_buf) or "*"
                path_buf.clear()
                pattern_buf.clear()
            elif ch == "(":
                if bracket_depth:
                    pattern_buf.append(ch)
                bracket_depth += 1
            elif ch == ")":
                if not bracket_depth:
                    raise ValueError("Found unmatched bracket.")
                bracket_depth -= 1
                if bracket_depth:
                    pattern_buf.append(ch)
            else:
                (pattern_buf if bracket_depth else path_buf).append(ch)
        if bracket_depth:
            raise ValueError("Found unmatched bracket.")
        if path_buf:
            patterns["".join(path_buf)] = "".join(pattern_buf) or "*"
        return (self.path if "land" in patterns else self.path_without_land) == ".".join(patterns) and all(
            k in self.pattern and v in ("*", self.pattern[k]) for k, v in patterns.items()
        )

    def expects(self, pattern: str) -> Self:
        if not self.follows(pattern):
            raise ValueError(f"Selector {self} does not follow {pattern}")

        return self

    def rev(self) -> ContextSelector:
        ctx = ctx_context.get(None)
        if ctx is None:
            raise LookupError
        return ctx.wrap(self)


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
