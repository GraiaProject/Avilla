from __future__ import annotations
from typing import TYPE_CHECKING, Any, Type, overload
from avilla.core.platform import Base

from avilla.core.metadata.source import MetadataSource
from avilla.core.utilles.selector import DepthSelector, Selector
from avilla.core.selectors import mainline


class MetaSelectorPrefix:
    type: Type[Selector]

    # common
    last: str | None = None

    # depth
    keypath: str | None = None

    # mainline
    platform: Base | None = None

    @overload
    def __init__(self, type: Type[Selector]) -> None:
        ...

    @overload
    def __init__(
        self, type: Type[DepthSelector], *, keypath: str | None = None, last: str | None = None
    ) -> None:
        ...

    @overload
    def __init__(
        self, type: Type[mainline], *, platform: Base | None = None, keypath: str | None = None
    ) -> None:
        ...

    def __init__(
        self,
        type: Type[Selector],
        *,
        last: str | None = None,
        keypath: str | None = None,
        platform: Base | None = None,
    ) -> None:
        self.type = type
        self.last = last
        self.keypath = keypath
        self.platform = platform

    def __hash__(self) -> int:
        return hash((self.type, self.last, self.keypath, self.platform))


class MetadataInterface:
    sources: dict[MetaSelectorPrefix | Type, MetadataSource]

    def __init__(self):
        self.sources = {}

    def register(self, prefix: MetaSelectorPrefix | Type, source: MetadataSource):
        if prefix in self.sources:
            raise ValueError(f"Prefix {prefix} already registered")
        self.sources[prefix] = source

    def get_source(self, target: Any):
        target_type = type(target)
        if not issubclass(target_type, Selector):
            return self.sources.get(target_type)
        if target_type is mainline:
            assert isinstance(target, mainline)
            keypath = target.keypath()
            last = target.last()
            platform = target.path.get("platform")
            for prefix in self.sources:
                if all(
                    (
                        isinstance(prefix, MetaSelectorPrefix),
                        prefix.type is mainline,
                        prefix.platform == platform if prefix.platform is not None else True,
                        prefix.keypath == keypath if prefix.keypath is not None else True,
                        prefix.last == last if prefix.last is not None else True,
                    )
                ):
                    return self.sources[prefix]
        elif issubclass(target_type, DepthSelector):
            for prefix in self.sources:
                if all(
                    (
                        isinstance(prefix, MetaSelectorPrefix),
                        prefix.type is target_type,
                        prefix.keypath == target.keypath() if prefix.keypath is not None else True,
                        prefix.last == target.last() if prefix.last is not None else True,
                    )
                ):
                    return self.sources[prefix]
        else:
            for prefix in self.sources:
                if all(
                    (
                        isinstance(prefix, MetaSelectorPrefix),
                        prefix.type is target_type,
                        prefix.last == target.last() if prefix.last is not None else True,
                    )
                ):
                    return self.sources[prefix]
        raise ValueError(f"No source found for {target}")
