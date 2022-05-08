from __future__ import annotations

from dataclasses import dataclass

from avilla.core.platform import Base
from avilla.core.resource import Resource, ResourceProvider


@dataclass
class ResourceMatchPrefix:
    resource_type: type[Resource]
    keypath: str | None = None
    platform: Base | None = None


class ResourceInterface:
    providers: dict[ResourceMatchPrefix, ResourceProvider]

    def __init__(self):
        self.providers = {}

    def register(
        self,
        resource_type: type[Resource],
        provider: ResourceProvider,
        *,
        mainline_keypath: str | None = None,
        platform: Base | None = None,
    ):
        self.providers[ResourceMatchPrefix(resource_type, mainline_keypath, platform)] = provider

    def get_provider(
        self,
        resource: Resource | type[Resource],
        *,
        mainline_keypath: str | None = None,
        platform: Base | None = None,
    ) -> ResourceProvider | None:
        resource_type = resource if isinstance(resource, type) else type(resource)
        for prefix in self.providers:
            if all((
                prefix.resource_type is resource_type,
                prefix.keypath == mainline_keypath if prefix.keypath is not None else True,
                prefix.platform == platform if prefix.platform is not None else True
            )):
                return self.providers[prefix]
