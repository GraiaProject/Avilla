from typing import Any, Dict


class SelectorKey:
    selector: str
    key: str
    past: Dict[str, Any]

    def __init__(self, selector: str, key: str, past: Dict[str, Any] = None):
        self.selector = selector
        self.key = key
        self.past = past or {}

    def __getitem__(self, value: Any):
        instance = Selector(self.selector, self.past)
        instance.path[self.key] = value
        return instance

    def __getattr__(self, addition_name: str):
        self.key += "." + addition_name
        return self

    def __repr__(self):
        return f"<{self.selector}>.{self.key}"


class SelectorMeta(type):
    def __getattr__(cls, key: str) -> "SelectorKey":
        return SelectorKey(cls.scope, key)  # type: ignore


class Selector(metaclass=SelectorMeta):
    scope: str
    path: Dict[str, Any]

    def __init__(self, scope: str, path: Dict[str, Any] = None) -> None:
        self.scope = scope
        self.path = path or {}

    def __getattr__(self, key: str) -> "SelectorKey":
        return SelectorKey(self.scope, key)

    def to_dict(self):
        return self.path

    def __repr__(self) -> str:
        return f"<{self.scope}>.{'.'.join([f'{k}[{v}]' for k, v in self.path.items()])}"
