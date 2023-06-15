from __future__ import annotations

from typing import TYPE_CHECKING

from ..resource import LocalFileResource, RawResource
from ..trait.context import fetch

if TYPE_CHECKING:
    from ..context import Context


@fetch(LocalFileResource)
async def fetch_localfile(cx: Context, res: LocalFileResource):
    return res.file.read_bytes()


@fetch(RawResource)
async def fetch_raw(cx: Context, res: RawResource):
    return res.data
