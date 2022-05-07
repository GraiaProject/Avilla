from __future__ import annotations

from abc import ABCMeta, abstractmethod
from typing import TYPE_CHECKING, Any, Awaitable, Callable, Dict, Type, TypeVar

if TYPE_CHECKING:
    from .model import Metadata, MetadataModifies


M = TypeVar("M", bound=Metadata)
T = TypeVar("T")

class MetadataSource(metaclass=ABCMeta):
    @abstractmethod
    async def fetch(self, target: Any, model: Type[M]) -> M:
        ...
    
    @abstractmethod
    async def modify(self, target: Any, modifies: MetadataModifies[T]) -> T:
        ...

class MetaSourceRegistrar:
    handlers: Dict[str, Dict[str, Callable]] = {}

    def __init__(self) -> None:
        self.handlers = {}

    def apply(self, source: Type[DispatchableSource]):
        source.handlers.update(self.handlers)
        return source
    
    def register(self, field: str, operator: str, handler: Callable) -> None:
        self.handlers.setdefault(field, {})
        self.handlers[field][operator] = handler

    def fetch(self, field: str):
        def warpper(self, handler: T_fetch):
            self.register(field, "fetch", handler)
            return handler
        return warpper

    def modify(self, field: str):
        def warpper(self, handler: T_modify):
            self.register(field, "modify", handler)
            return handler
        return warpper

T_fetch = Callable[[Any, list[str]], dict[str, Any]]
T_modify = Callable[[Any, MetadataModifies[T]], T]

class DispatchableSource(MetadataSource):
    handlers: Dict[str, Dict[str, Callable]] = {}

    def __init_subclass__(cls, **kwargs):
        cls.handlers = {}
        for base in reversed(cls.__bases__):
            if issubclass(base, DispatchableSource):
                cls.handlers.update(base.handlers)

    async def fetch(self, target: Any, model: Type[M]) -> M:
        fields = model.fields()
        fields = map(lambda a: a.id, fields)
        if not set(fields).issubset(self.handlers):
            not_implemented = set(fields).difference(self.handlers)
            raise NotImplementedError(f"{model.__name__} has not implemented {not_implemented}")
        handle_mapping = {}
        for field in fields:
            handlers = self.handlers[field]
            if "fetch" not in handlers:
                raise NotImplementedError(f"{model.__name__} has not implemented .fetch for {field}")
            handler = handlers["fetch"]
            handle_mapping.setdefault(handler, []).append(field)
        result = {}
        for handler, fields in handle_mapping.items():
            result.update(await handler(target, fields))
        return model(content=result)

    async def modify(self, target: Any, modifies: MetadataModifies[T]) -> T:
        fields = modifies.modified
        if not set(fields).issubset(self.handlers):
            not_implemented = set(fields).difference(self.handlers)
            raise NotImplementedError(f"{modifies.__class__.__name__} has not implemented {not_implemented}")
        handle_mapping = {}
        for field in fields:
            if field in handle_mapping:
                raise TypeError(f"{field} is conflicted, check the declaration.")
            handlers = self.handlers[field]
            if "modify" not in handlers:
                raise NotImplementedError(f"{modifies.__class__.__name__} has not implemented .modify for {field}")
            handler: Callable[[Any, str, Any, Any], Awaitable[T]] = handlers["modify"]
            handle_mapping[field] = handler
        if not handle_mapping:
            raise TypeError("not any field to modify.")
        for field, handler in handle_mapping.items():
            result = await handler(target, field, modifies.past[field], modifies.current[field])
        return result  # type: ignore
