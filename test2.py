from typing import List, Set
import random
from graia.broadcast.utilles import printer

class LaunchComponent:
    id: str
    required: Set[str]

    def __init__(self, id, required=None):
        if required is None:
            required = set()
        self.id = id
        self.required = required

    def __repr__(self):
        return f'LaunchComponent(id={self.id},required={self.required})'


l1 = LaunchComponent(0)
l2 = LaunchComponent(1, {0})
l3 = LaunchComponent(2, {0, 1, 3})
l4 = LaunchComponent(3)
l5 = LaunchComponent(4, {2, 3})
l6 = LaunchComponent(5, {4,1})
l7 = LaunchComponent(6, {5,2,1})
l8 = LaunchComponent(7, {6,1})
l9 = LaunchComponent(8, {7, 1, 2})
l10 = LaunchComponent(9, {5, 6, 7})
l11 = LaunchComponent(10, {2,3,6})
l12 = LaunchComponent(11, {0,1,4,5})
l13 = LaunchComponent(12, {0,1,4,5})
components = [l1, l2, l3, l4, l5, l6, l7, l8, l9, l10, l11, l12, l13]
random.shuffle(components)

def resolve_requirements(components: List[LaunchComponent]) -> List[List[LaunchComponent]]:
    resolved = set()
    result = []
    while components:
        layer = []
        for component in components:
            if component.required.issubset(resolved):
                layer.append(component)
        if layer:
            for component in layer:
                components.remove(component)
            resolved.update(component.id for component in layer)
            result.append(layer)
        else:
            raise Exception
    return result

from rich import print
print("original: ", components)
print("resolve: ", resolve_requirements(components))