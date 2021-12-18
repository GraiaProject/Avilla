from dataclasses import dataclass
from datetime import datetime as dt
from typing import Any, Dict, List, Optional, Tuple, Union

from avilla.core.selectors import entity as rsctx_selector
from avilla.core.selectors import mainline as mainline_selector


@dataclass
class Node:
    id: str
    defaults: Dict[str, bool]


@dataclass
class Rank:
    id: str
    mixins: List[str]


@dataclass
class Rule:
    target: Union[rsctx_selector, mainline_selector, str]
    context: Dict[str, Any]
    pattern: str
    value: bool
    period: Tuple[Optional[dt], Optional[dt]] = (None, None)
