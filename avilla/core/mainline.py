"""Mainline 用于单纯的用字符串描述 Relationship.exec.to 的作用对象.

Example:

```py
from avilla.core.mainline import mainline

rs.exec(MessageSend(...)).to(
    mainline.group['9413245365']
)
rs.exec(MessageSend(...)).to(
    mainline.channel['9413245365'].guild['950455422']
)
```

mainline 有一个方便的方法 `to_dict`, 用于将其本身转换为字典.

```py
assert mainline.channel['9413245365'].guild['950455422'] == {
    "channel": "9413245365",
    "guild": "950455422"
}
```
"""


from typing import Dict, Type


class MainlineItemSetter:
    mainline: "Mainline"
    key: str

    def __init__(self, mainline: "Mainline", key: str):
        self.mainline = mainline
        self.key = key

    def __getitem__(self, value: str) -> "Mainline":
        self.mainline.path[self.key] = value
        return self.mainline


class MainlineMeta(type):
    def __getattr__(cls: Type["Mainline"], key: str) -> "MainlineItemSetter":  # type: ignore
        return MainlineItemSetter(cls(), key)


class Mainline(metaclass=MainlineMeta):
    path: Dict[str, str]

    def __init__(self):
        self.path = {}

    def __getattr__(self, key: str) -> "MainlineItemSetter":
        return MainlineItemSetter(self, key)

    def to_dict(self) -> dict:
        return self.path

    def __repr__(self) -> str:
        return ".".join(["mainline", *[f"{k}[{v}]" for k, v in self.path.items()]])


mainline = Mainline
