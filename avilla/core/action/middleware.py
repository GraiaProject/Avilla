from __future__ import annotations

import abc
from typing import TYPE_CHECKING, Any, AsyncContextManager

if TYPE_CHECKING:
    from avilla.core.relationship import RelationshipExecutor


class ActionMiddleware(abc.ABC):
    async def before_execute(self, executor: RelationshipExecutor) -> Any:
        ...

    async def before_extensions_apply(self, executor: RelationshipExecutor, params: dict[str, Any] | None) -> Any:
        ...

    async def on_params_ready(self, executor: RelationshipExecutor, params: dict[str, Any] | None) -> Any:
        ...

    @abc.abstractmethod
    def lifespan(self, executor: RelationshipExecutor) -> AsyncContextManager:
        ...
