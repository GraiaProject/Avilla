from dataclasses import dataclass
from typing import Any, Dict, List, Optional, Tuple, Union
from avilla.core.selectors import rsctx as rsctx_selector, mainline as mainline_selector
from datetime import datetime as dt


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
