import typing
from dataclasses import dataclass


@dataclass
class Policy(typing.Protocol):
    pass
