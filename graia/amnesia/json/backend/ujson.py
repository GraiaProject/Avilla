from __future__ import annotations

from typing import Any

import ujson

from graia.amnesia.json import JSONBackend, TJson, TJsonCustomSerializer
from graia.amnesia.json.serializers import DEEP_OBJ_SCAN, SERIALIZERS


class UJsonBackend(JSONBackend):
    def serialize(self, value: Any, *, custom_serializers: dict[type, TJsonCustomSerializer] | None = None) -> str:
        return ujson.dumps(
            DEEP_OBJ_SCAN(value, custom_serializers and dict(SERIALIZERS, **custom_serializers) or SERIALIZERS)
        )

    def deserialize(self, value: str) -> TJson:
        return ujson.loads(value)


BACKEND_INSTANCE = UJsonBackend()
