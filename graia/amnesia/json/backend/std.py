from __future__ import annotations

import json
from functools import partial
from typing import Any

from .. import JSONBackend, TJson, TJsonCustomSerializer
from ..serializers import SERIALIZER_DEFAULT, SERIALIZERS


class StdBackend(JSONBackend):
    def serialize(self, value: Any, *, custom_serializers: dict[type, TJsonCustomSerializer] | None = None) -> str:
        return json.dumps(
            value,
            default=partial(
                SERIALIZER_DEFAULT, d=custom_serializers and dict(SERIALIZERS, **custom_serializers) or SERIALIZERS
            ),
        )

    def deserialize(self, value: str) -> TJson:
        return json.loads(value)


BACKEND_INSTANCE = StdBackend()
