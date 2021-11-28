from dataclasses import dataclass
from typing import Generic

from . import TMetadata, TPolicy


@dataclass
class Endpoint(Generic[TMetadata, TPolicy]):
    policy: TPolicy
    metadata: TMetadata
