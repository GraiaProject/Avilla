import abc
from typing import Any, Generic, Type, TypeVar

T_Receive = TypeVar("T_Receive")
T_Value = TypeVar("T_Value")

T_Children = TypeVar("T_Children")


class Transformer(Generic[T_Receive, T_Value], abc.ABC):
    parent: "Transformer[Any, T_Receive]"

    @classmethod
    def create(cls, parent: "Transformer[Any, T_Receive]") -> "Transformer[T_Receive, T_Value]":
        instance = cls()
        instance.parent = parent
        return instance

    @abc.abstractmethod
    def transform(self) -> T_Value:
        raise NotImplementedError()

    def passby(self, transformer: "Type[Transformer[T_Value, T_Children]]") -> "Transformer[T_Value, T_Children]":
        return Transformer.create(self)


T_Origin = TypeVar("T_Origin")


class OriginProvider(Transformer[Any, T_Origin]):
    raw: T_Origin

    def __init__(self, raw: T_Origin) -> None:
        self.raw = raw

    @classmethod
    def create(cls, parent: "Transformer[Any, T_Receive]") -> "Transformer[Any, T_Origin]":
        raise NotImplementedError()

    def transform(self) -> T_Origin:
        return self.raw
