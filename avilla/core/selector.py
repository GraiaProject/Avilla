from __future__ import annotations

import re
from collections.abc import Callable, Mapping
from copy import deepcopy
from dataclasses import dataclass
from itertools import filterfalse
from types import MappingProxyType
from typing import Protocol, runtime_checkable

from typing_extensions import Self, TypeAlias

from avilla.core.platform import Land

EMPTY_MAP = MappingProxyType({})
ESCAPE = {")": "\\)", "(": "\\(", "]": "\\]", "[": "\\[", "}": "\\}", "{": "\\{"}

_follows_pattern = re.compile(r"(?P<name>(\w+?|[*~]))(#(?P<predicate>\w+))?(\((?P<literal>[^#]+?)\))?")
FollowsPredicater: TypeAlias = "Callable[[str], bool]"


@dataclass
class _FollowItem:
    name: str
    literal: str | None = None
    predicate: FollowsPredicater | None = None


def _parse_follows_item(item: str, items: dict[str, _FollowItem], predicates: dict[str, FollowsPredicater]):
    if item.startswith("::"):
        if "land" in items:
            raise ValueError("land already exists")
        item = item[2:]
        items["land"] = _FollowItem("land")
        if not item.strip():
            return
    if "*" in items:
        raise ValueError("wildcard already exists, no more items allowed")
    if not (m := _follows_pattern.fullmatch(item)):
        raise ValueError(f"invalid item: {item}")
    name = m["name"]
    if name == "~" and items:
        raise ValueError("inherit can only be the first item and only one")
    if m["literal"] and m["predicate"]:
        raise ValueError(f"duplicate literal and predicate: {item}")
    if m["literal"] is not None:
        literal = m["literal"].translate(str.maketrans(ESCAPE))
    else:
        literal = None
    predicate = predicates.get(m["predicate"]) if m["predicate"] else None
    items[name] = _FollowItem(name, literal, predicate)


def _parse_follows(pattern: str, **kwargs: FollowsPredicater) -> list[_FollowItem]:
    items = {}
    item = ""
    bracket_stack = []
    for i, char in enumerate(pattern):
        if char == "." and not bracket_stack:
            _parse_follows_item(item, items, kwargs)
            item = ""
            continue
        if char == "(":
            bracket_stack.append(i)
        elif char == ")":
            if not bracket_stack:
                raise ValueError(f"Unclosed parenthesis: {item})")
            bracket_stack.pop()
        item += char
    if bracket_stack:
        raise ValueError(f"Unclosed parenthesis: {pattern[bracket_stack[0]:]}")
    if item:
        _parse_follows_item(item, items, kwargs)
    return list(items.values())


class Selector:
    pattern: Mapping[str, str]

    def __init__(self, pattern: Mapping[str, str] = EMPTY_MAP) -> None:
        self.pattern = MappingProxyType({k: str(v) for k, v in pattern.items()})
        self._hash = hash(("Selector", *self.pattern.items()))

    def modify(self, pattern: Mapping[str, str]) -> Self:
        return self.__class__(pattern=pattern)

    def __getattr__(self, name: str) -> Callable[[str], Self]:
        if name.startswith("__"):
            return super().__getattribute__(name)  # type: ignore

        def wrapper(content: str) -> Self:
            return self.modify({**self.pattern, name: str(content)})

        return wrapper

    def __hash__(self) -> int:
        return self._hash

    def __eq__(self, o: object) -> bool:
        return isinstance(o, self.__class__) and o._hash == self._hash

    def __contains__(self, key: str) -> bool:
        return key in self.pattern

    def __getitem__(self, key: str) -> str:
        return self.pattern[key]

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}().{'.'.join(f'{k}({v})' for k, v in self.pattern.items())}"

    def __copy__(self):
        return self.modify({**self.pattern})

    def __deepcopy__(self, memo):
        data = {**self.pattern}
        return self.__class__(deepcopy(data, memo))

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
    def display(self) -> str:
        return ".".join(f"{k}({v})" for k, v in self.pattern.items())

    @property
    def display_without_land(self) -> str:
        return ".".join(f"{k}({v})" for k, v in self.pattern.items() if k != "land")

    @property
    def last_key(self) -> str:
        return next(reversed(self.pattern.keys()))

    @property
    def last_value(self) -> str:
        return next(reversed(self.pattern.values()))

    def items(self):
        return self.pattern.items()

    def appendix(self, key: str, value: str):
        return self.modify({**self.pattern, key: str(value)})

    def land(self, land: Land | str):
        if isinstance(land, Land):
            land = land.name

        return self.modify({"land": land, **{k: v for k, v in self.pattern.items() if k != "land"}})

    def to_selector(self):
        return self

    @classmethod
    def from_follows(cls, pattern: str):
        items = _parse_follows(pattern)
        mapping = {}
        for i in items:
            if i.literal is None:
                raise ValueError("literal expected")
            mapping[i.name] = i.literal
        return cls(mapping)

    from_follows_pattern = from_follows

    def follows(self, pattern: str, **kwargs: FollowsPredicater) -> bool:
        items = _parse_follows(pattern, **kwargs)
        index = 0
        for index, (item, name, value) in enumerate(zip(items, self.pattern.keys(), self.pattern.values())):
            if item.name == "*":
                return True
            if item.name != name:
                return False
            if item.predicate is not None and not item.predicate(value):
                return False
            if item.literal is not None and value != item.literal:
                return False
        return index + 1 == len(self.pattern)

    def into(self, pattern: str, **kwargs: str) -> Self:
        items = _parse_follows(pattern)
        new_patterns = {}
        iterator = iter(self.pattern)
        if items and items[0].name == "~":
            if not all(item.literal or kwargs.get(item.name) for item in items[1:]):
                raise ValueError("expected specific literals in follows pattern")
            return self.modify(
                {
                    **self.pattern,
                    **{item.name: kwargs.get(item.name) or item.literal for item in items[1:]},
                }  # type: ignore
            )
        for item in items:
            if item.name == "*":
                raise TypeError("expected no wildcard")
            current_key = next(iterator)
            if item.name != current_key:
                raise ValueError(f"expected {'.'.join(new_patterns)}.{item.name}, got {current_key}")
            new_patterns[current_key] = kwargs.get(item.name) or item.literal or self.pattern[current_key]
        return self.modify(new_patterns)

    def expects(
        self,
        pattern: str,
        *,
        exception_type: type[Exception] = ValueError,
        **kwargs: FollowsPredicater,
    ) -> Self:
        if not self.follows(pattern, **kwargs):
            raise exception_type(f"Selector {self} does not follow {pattern}")

        return self


@runtime_checkable
class Selectable(Protocol):
    def to_selector(self) -> Selector:
        ...
