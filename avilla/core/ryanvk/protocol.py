from __future__ import annotations

from typing import Any, Protocol

from typing_extensions import TypeVar

VnEventRaw = TypeVar("VnEventRaw", default=dict, infer_variance=True)
VnElementRaw = TypeVar("VnElementRaw", default=dict, infer_variance=True)


class SupportsArtifacts(Protocol):
    def get_staff_artifacts(self) -> list[dict[Any, Any]]:
        ...


class SupportsComponent(Protocol):
    def get_staff_components(self) -> dict[str, SupportsArtifacts]:
        ...


class SupportsStaff(SupportsArtifacts, SupportsComponent, Protocol[VnElementRaw, VnEventRaw]):
    def __staff_generic__(self, element_type: VnElementRaw, event_type: VnEventRaw):
        ...
