from __future__ import annotations

from typing import TYPE_CHECKING, Any, TypedDict, final

from .scoped import scoped_collect

if TYPE_CHECKING:
    from .context import CollectContext


class EntityAssignInfo(TypedDict, total=False):
    cls: type
    name: str
    annotation: Any


class BaseEntity:
    collect_context: CollectContext | None = None

    def collect(self, collector: CollectContext):
        self.collect_context = collector

        if isinstance(self.collect_context, scoped_collect):
            self.collect_context.on_collected(self._fallback_collected_callback)

        return self

    def assign_callback(self, info: EntityAssignInfo):
        ...

    @final
    def _fallback_collected_callback(self, collector):
        self.assign_callback({})

    def __set_name__(self, owner: type, name: str):
        if self.collect_context is None:
            return

        if isinstance(self.collect_context, scoped_collect):
            if owner is not self.collect_context.cls:
                return

            try:
                self.collect_context.remove_collected_callback(self._fallback_collected_callback)
            except ValueError:
                pass

            @self.collect_context.on_collected
            def _(collector: scoped_collect):
                if collector.cls is None:
                    return

                if name in collector.cls.__annotations__:
                    self.assign_callback({"cls": collector.cls, "name": name, "annotation": collector.cls.__annotations__[name]})
                else:
                    self.assign_callback({"cls": collector.cls, "name": name})
