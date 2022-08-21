from __future__ import annotations

import abc
from typing import TYPE_CHECKING, Any

from .context import get_current_namespace

if TYPE_CHECKING:
    from avilla.core.traitof.signature import ArtifactSignature


class Recorder(abc.ABC):
    @abc.abstractmethod
    def signature(self) -> ArtifactSignature:
        ...

    def __call__(self, content: Any):
        sig = self.signature()
        r = get_current_namespace()
        r[sig] = content
        return content
