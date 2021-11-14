from dataclasses import dataclass
from typing import Generic
from . import M, P


@dataclass
class Endpoint(Generic[M, P]):
    policy: P
    metadata: M
