from typing import TYPE_CHECKING, Any, ClassVar, Dict, Generic, Optional, Set, Type, TypeVar, Union, cast

T = TypeVar("T")
A = TypeVar("A")


class SelectorKey(Generic[A, T]):
    selector: "Type[Selector]"
    key: str
    past: Dict[str, Any]

    def __init__(self, selector: "Type[Selector]", key: str, past: Optional[Dict[str, Any]] = None):
        self.selector = selector
        self.key = key
        self.past = past or {}

    def __getitem__(self, value: T) -> A:
        instance = self.selector(self.past)
        instance.path[self.key] = value
        return cast(A, instance)

    def __getattr__(self, addition_name: str):
        # sourcery skip: use-fstring-for-concatenation
        self.key += "." + addition_name
        return self

    def __repr__(self):
        return f"<{self.selector}>.{self.key}"


class SelectorMeta(type):
    if TYPE_CHECKING:
        scope: str

    def __getattr__(cls, key: str) -> "SelectorKey":
        # sourcery skip: instance-method-first-arg-name
        return SelectorKey(cls, key)  # type: ignore


S = TypeVar("S", bound=str)


class Selector(Generic[S], metaclass=SelectorMeta):
    scope: S
    path: Dict[str, Any]

    def __init__(self, path: Optional[Dict[str, Any]] = None) -> None:
        self.path = path or {}

    def to_dict(self):
        return self.path

    def last(self) -> Any:
        return list(self.path.items())[-1]

    def __repr__(self) -> str:
        return f"<{self.scope}>.{'.'.join([f'{k}[{v}]' for k, v in self.path.items()])}"

    def __getitem__(self, value: str):
        return self.path[value]

    def __getattr__(self, key: str) -> "Union[SelectorKey, Any]":
        return SelectorKey(self.__class__, key, self.path)

    def __eq__(self, __o: object) -> bool:
        # sourcery skip: assign-if-exp, comprehension-to-generator, reintroduce-else, swap-if-expression
        if not isinstance(__o, Selector):
            return False
        return self.scope == __o.scope and all([__o[k] == v for k, v in self.path.items()])

    def __and__(self, __o: "Selector") -> bool:
        if self.scope != __o.scope:
            return False
        return all(v == __o.path[k] for k, v in self.path.items() if k in __o.path)

    def __hash__(self) -> int:
        return hash(tuple(self.path.items()))


class DepthSelector(Selector):
    _keypath_excludes: "ClassVar[frozenset[str]]" = frozenset()

    def keypath(self, exclude: Set[str] = frozenset()) -> str:  # type: ignore
        return ".".join([k for k in self.path.keys() if k not in set(*exclude, *self._keypath_excludes)])
