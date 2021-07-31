import abc
from typing import Any, Generic, Type, TypeVar

T_Receive = TypeVar("T_Receive")
T_Value = TypeVar("T_Value")

T_Children = TypeVar("T_Children")


class Transformer(Generic[T_Receive, T_Value], abc.ABC):
    received: "Transformer[Any, T_Receive]"

    @classmethod
    def create(cls, received: "Transformer[Any, T_Receive]", *args, **kwargs) -> "Transformer[T_Receive, T_Value]":
        instance = cls()
        instance.received = received
        instance.__post_init__(*args, **kwargs)
        return instance

    def __post_init__(self, *args, **kwargs):
        pass

    @abc.abstractmethod
    def transform(self) -> T_Value:
        raise NotImplementedError()

    def passby(
        self, transformer: "Type[Transformer[T_Value, T_Children]]", *args, **kwargs
    ) -> "Transformer[T_Value, T_Children]":
        return transformer.create(self, *args, **kwargs)


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


import json


class Utf8StringTransformer(Transformer[bytes, str]):
    def transform(self) -> str:
        return self.received.transform().decode("utf-8")


class BytesDecodeTransformer(Transformer[bytes, str]):
    encoding: str

    def __post_init__(self, encoding: str) -> None:
        self.encoding = encoding

    def transform(self) -> str:
        return self.received.transform().decode(self.encoding)


class JsonTransformer(Transformer[str, Any]):
    def transform(self) -> Any:
        return json.loads(self.received.transform())
