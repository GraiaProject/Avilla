from dataclasses import dataclass
import typing


@dataclass
class Policy(typing.Protocol):
    pass
