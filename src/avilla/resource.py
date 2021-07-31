from typing import Generic, TypeVar
from .provider import Provider

T_Provider = TypeVar("T_Provider", bound=Provider)


class Resource(Generic[T_Provider]):
    provider: T_Provider

    def __init__(self, provider: T_Provider):
        self.provider = provider
