from typing import TYPE_CHECKING, Any, Awaitable, Callable, List, Optional, Set

if TYPE_CHECKING:
    from avilla.core import Avilla


class LaunchComponent:
    id: str
    required: Set[str]

    prepare: Optional[Callable[["Avilla"], Awaitable[Any]]] = None
    mainline: Optional[Callable[["Avilla"], Awaitable[Any]]] = None
    cleanup: Optional[Callable[["Avilla"], Awaitable[Any]]] = None

    def __init__(
        self,
        component_id: str,
        required: Set[str],
        mainline: Optional[Callable[["Avilla"], Awaitable[Any]]] = None,
        prepare: Optional[Callable[["Avilla"], Awaitable[Any]]] = None,
        cleanup: Optional[Callable[["Avilla"], Awaitable[Any]]] = None,
    ):
        self.id = component_id
        self.required = required
        self.mainline = mainline
        self.prepare = prepare
        self.cleanup = cleanup


class RequirementResolveFailed(Exception):
    pass


def resolve_requirements(components: Set[LaunchComponent]) -> List[Set[LaunchComponent]]:
    resolved = set()
    result = []
    while components:
        layer = set()
        for index, component in enumerate(components):
            if component.required.issubset(resolved):
                layer.add(component)
        if layer:
            components -= layer
            resolved.update(component.id for component in layer)
            result.append(layer)
        else:
            raise RequirementResolveFailed
    return result
