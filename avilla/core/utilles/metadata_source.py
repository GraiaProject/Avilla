from __future__ import annotations

import inspect
from typing import TYPE_CHECKING, Callable, ClassVar, Coroutine, Generic, TypeVar, cast

from typing_extensions import Self

from avilla.core.metadata.model import Metadata, Modify
from avilla.core.metadata.source import MetadataSource
from avilla.core.utilles.selector import Selector

if TYPE_CHECKING:
    from avilla.core.protocol import BaseProtocol

Fetcher = Callable[["DispatachingMetadataSource", Selector, type[Metadata]], Coroutine[None, None, Metadata]]
Modifier = Callable[["DispatachingMetadataSource", Selector, list[Modify]], Coroutine[None, None, Metadata]]


def fetch(*model_types: type[Metadata]):
    def decorator(func: Fetcher):
        if not hasattr(func, "__fetch_metadata_types__"):
            func.__fetch_metadata_types__ = []
        func.__fetch_metadata_types__.extend(model_types)
        return func

    return decorator


def modify(*model_types: type[Metadata]):
    def decorator(func: Fetcher):
        if not hasattr(func, "__modify_metadata_types__"):
            func.__modify_metadata_types__ = []
        func.__modify_metadata_types__.extend(model_types)
        return func

    return decorator


# 先对比 Target (Selector.match), 再到对特定 target 实现的 source.
# 第一步的对比由 Protocol.get_metadata_source 完成, Source 仅提供 Target Pattern.


class DispatachingMetadataSource(MetadataSource[Selector]):
    pattern: ClassVar[Selector] = Selector(mode="any")
    fetchers: ClassVar[
        dict[type[Metadata], Callable[[Self, Selector, type[Metadata]], Coroutine[None, None, Metadata]]]
    ] = {}
    modifiers: ClassVar[
        dict[type[Metadata], Callable[[Self, Selector, list[Modify]], Coroutine[None, None, Metadata]]]
    ] = {}

    def __init_subclass__(cls, pattern: Selector) -> None:
        super().__init_subclass__()
        cls.pattern = pattern
        cls.fetchers = {}
        cls.modifiers = {}
        for mro in reversed(inspect.getmro(cls)):
            if issubclass(mro, DispatachingMetadataSource):
                cls.fetchers.update(mro.fetchers)
                cls.modifiers.update(mro.modifiers)
        for _, member in inspect.getmembers(cls):
            if callable(member) and hasattr(member, "__fetch_metadata_types__"):
                for model_type in member.__fetch_metadata_types__:
                    cls.fetchers[model_type] = member
            elif callable(member) and hasattr(member, "__modify_metadata_types__"):
                for model_type in member.__modify_metadata_types__:
                    cls.modifiers[model_type] = member

    async def fetch(self, target: Selector, model: type[Metadata]):
        if not self.pattern.match(target):
            raise ValueError(f"Target {target} does not match {self.pattern}.")
        fetcher = self.fetchers.get(model)
        if fetcher is None:
            raise NotImplementedError(f"Fetcher for {model} is not implemented.")
        return await fetcher(self, target, model)

    async def modify(self, target: Selector, modifies: list[Modify]):
        if not self.pattern.match(target):
            raise ValueError(f"Target {target} does not match {self.pattern}.")
        modifier = self.modifiers.get(modifies.model)
        if modifier is None:
            raise NotImplementedError(f"Modifier for {modifies.model} is not implemented.")
        return await modifier(self, target, modifies)


_P = TypeVar("_P", bound="BaseProtocol")


class ProtocolMetadataSource(DispatachingMetadataSource, Generic[_P], pattern=Selector(mode="any")):
    protocol: _P

    def __init_subclass__(cls, pattern: Selector) -> None:
        return super().__init_subclass__(pattern)

    def __init__(self, protocol: _P):
        self.protocol = protocol
