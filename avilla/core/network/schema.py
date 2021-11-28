from typing import Any, Generic

from . import TMetadata


class Schema(Generic[TMetadata]):
    pattern: Any  # 调用 Endpoint 的规则
