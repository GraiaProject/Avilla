from __future__ import annotations

from typing import TYPE_CHECKING

from ..resource import LocalFileResource
from ..trait.context import fetch

if TYPE_CHECKING:
    from ..context import Context


@fetch(LocalFileResource)
async def fetch_localfile(ctx: Context, res: LocalFileResource):
    return res.file.read_bytes()
