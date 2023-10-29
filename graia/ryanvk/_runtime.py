from __future__ import annotations

from collections import ChainMap
from itertools import chain
from typing import Any

from graia.ryanvk.typing import SupportsMerge

GLOBAL_GALLERY = {}  # layout: {namespace: {identify: {...}}}, cover-mode.


def ref(namespace: str, identify: str | None = None) -> dict[Any, Any]:
    ns = GLOBAL_GALLERY.setdefault(namespace, {})
    scope = ns.setdefault(identify or "_", {})
    return scope


def merge(*artifacts: dict[Any, Any]):
    chainmap = ChainMap(*artifacts)
    total_signatures = list(dict.fromkeys(chain(*[i.keys() for i in artifacts])))
    result = {}

    for sign in total_signatures:
        if isinstance(sign, SupportsMerge):
            records = [i[sign] for i in artifacts if sign in i]
            result[sign] = sign.merge(*records)
        else:
            result[sign] = chainmap[sign]

    return result
