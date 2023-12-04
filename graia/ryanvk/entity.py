from __future__ import annotations

from typing import Any, TypedDict

from typing_extensions import NotRequired

from ryanvk.collector import BaseCollector
from ryanvk.perform import BasePerform


class EntityAssignInfo(TypedDict):
    name: NotRequired[str]
    annotation: NotRequired[Any]


class BaseEntity:
    collector: BaseCollector | None = None

    def collect(self, collector: BaseCollector):
        self.collector = collector
        self.collector.on_collected(self._fallback_collected_callback)

        return self

    def assign_callback(self, info: EntityAssignInfo):
        ...

    def _fallback_collected_callback(self, cls: type):
        self.assign_callback({})

    def __set_name__(self, owner: type, name: str):
        assert self.collector is not None

        if not issubclass(owner, BasePerform):
            return

        try:
            self.collector.remove_collected_callback(self._fallback_collected_callback)
        except ValueError:
            pass

        @self.collector.on_collected
        def collected_callback(cls: type):
            if name in cls.__annotations__:
                self.assign_callback({"name": name, "annotation": cls.__annotations__[name]})
            else:
                self.assign_callback({"name": name})
