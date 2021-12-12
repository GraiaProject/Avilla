import json
from typing import Any, Callable


def u8_string(binary: bytes) -> str:
    """
    Convert a binary string to a unicode string.
    """
    return binary.decode("utf-8")


def u8_encode(data: str) -> bytes:
    return data.encode("utf-8")


def binary_decode(pattern: str):
    def decoder(binary: bytes) -> str:
        return binary.decode(pattern)

    return decoder


def json_encode(json_encoder: Callable[[Any], str] = json.dumps):
    def encoder(obj) -> str:
        return json_encoder(obj)

    return encoder


def json_decode(json_decoder: Callable[[str], Any] = json.loads):
    def decoder(json_string) -> Any:
        return json_decoder(json_string)

    return decoder
