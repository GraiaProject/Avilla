from __future__ import annotations

from typing import Any

from graia.amnesia.json import TJson

from .bootstrap import CURRENT_BACKEND


class Json:
    @staticmethod
    def serialize_as_bytes(obj: Any) -> bytes:
        return CURRENT_BACKEND.serialize_as_bytes(obj)

    @staticmethod
    def serialize(obj: Any) -> str:
        return CURRENT_BACKEND.serialize(obj)

    @staticmethod
    def deserialize(content: str) -> TJson:
        return CURRENT_BACKEND.deserialize(content)
