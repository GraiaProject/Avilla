from __future__ import annotations

import functools
from collections import defaultdict
from contextvars import ContextVar, copy_context
from typing import Any, Callable, Generator, Tuple

from .context import CollectContext, InstanceContext
from .typing import P, R, TEntity

GLOBAL_COLLECT_CONTEXT = CollectContext()
GLOBAL_INSTANCE_CONTEXT = InstanceContext()

COLLECTING_CONTEXT_VAR = ContextVar("CollectingContext", default=GLOBAL_COLLECT_CONTEXT)
LOOKUP_LAYOUT_VAR = ContextVar[Tuple[CollectContext, ...]]("LookupContext", default=(GLOBAL_COLLECT_CONTEXT,))
INSTANCE_CONTEXT_VAR = ContextVar("InstanceContext", default=GLOBAL_INSTANCE_CONTEXT)

ITER_BUCKET_VAR: ContextVar[defaultdict[Any, list[int]]] = ContextVar("LAYOUT_ITER_COLLECTIONS")


def _standalone_context(func: Callable[P, R]) -> Callable[P, R]:
    @functools.wraps(func)
    def wrapper(*args: P.args, **kwargs: P.kwargs) -> R:
        return copy_context().run(func, *args, **kwargs)

    return wrapper


@_standalone_context
def iter_layout(session_id: Any | None = None) -> Generator[CollectContext, None, None]:
    bucket = ITER_BUCKET_VAR.get(None)
    if bucket is None:
        bucket = defaultdict(lambda: [-1])
        ITER_BUCKET_VAR.set(bucket)

    stack = bucket[session_id]

    contexts = LOOKUP_LAYOUT_VAR.get()
    index = stack[-1]
    stack.append(index)

    try:
        for content in contexts[index + 1 :]:
            stack[-1] += 1
            yield content
    finally:
        stack.pop()
        if not stack:
            bucket.pop(session_id, None)


def global_collect(entity: TEntity) -> TEntity:
    return GLOBAL_COLLECT_CONTEXT.collect(entity)


def local_collect(entity: TEntity) -> TEntity:
    return COLLECTING_CONTEXT_VAR.get().collect(entity)
