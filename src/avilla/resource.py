from typing import Generic

from avilla.typing import T_Provider


class Resource(Generic[T_Provider]):
    provider: T_Provider

    def __init__(self, provider: T_Provider):
        self.provider = provider
