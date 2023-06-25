from __future__ import annotations

from dataclasses import dataclass

from graia.saya.behaviour import Behaviour
from graia.saya.cube import Cube
from graia.saya.schema import BaseSchema

from launart import Launart, Launchable


@dataclass
class LaunchableSchema(BaseSchema):
    pass


class LaunartBehaviour(Behaviour):
    manager: Launart

    def __init__(self, manager: Launart) -> None:
        self.manager = manager

    def allocate(self, cube: Cube[LaunchableSchema]):
        if isinstance(cube.metaclass, LaunchableSchema):
            if not isinstance(cube.content, Launchable):
                raise TypeError(f"{cube.content} is not a Launchable")
            self.manager.add_launchable(cube.content)
        else:
            return
        return True

    def release(self, cube: Cube[LaunchableSchema]):
        if isinstance(cube.metaclass, LaunchableSchema):
            self.manager.remove_launchable(cube.content)
        else:
            return
        return True

    uninstall = release
