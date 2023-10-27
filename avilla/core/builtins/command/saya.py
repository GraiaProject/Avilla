from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Callable, List, Optional, Union

from arclet.alconna import Alconna, CommandMeta
from arclet.alconna.args import Arg, Args, TAValue
from arclet.alconna.tools import AlconnaString
from graia.broadcast.entities.decorator import Decorator
from graia.broadcast.entities.dispatcher import BaseDispatcher
from graia.saya.behaviour import Behaviour
from graia.saya.cube import Cube
from graia.saya.schema import BaseSchema
from pygtrie import _NoChildren

from . import AvillaCommands


class Command(AlconnaString, BaseSchema):
    def __init__(
        self,
        command: str,
        help_text: Optional[str] = None,
        dispatchers: Optional[List[BaseDispatcher]] = None,
        decorators: Optional[List[Decorator]] = None,
    ):
        super().__init__(command, help_text)
        self.dispatchers = dispatchers or []
        self.decorators = decorators or []

    def register(self, func: Callable, cmd: AvillaCommands):
        """注册 func 至 AvillaCommands

        Args:
            func (Callable): 命令函数
            cmd (AvillaCommands): 命令对象
        """
        cmd.on(self.build(), self.dispatchers, self.decorators)(func)  # type: ignore


@dataclass
class On(BaseSchema):
    """命令监听 Schema, 相当于 avilla_commands.on"""

    command: Union[str, Alconna]
    dispatchers: List[BaseDispatcher] = field(default_factory=list)
    decorators: List[Decorator] = field(default_factory=list)
    args: Optional[dict[str, Union[TAValue, Args, Arg]]] = field(default=None)
    meta: Optional[CommandMeta] = field(default=None)

    def register(self, func: Callable, cmd: AvillaCommands):
        """注册 func 至 AvillaCommands

        Args:
            func (Callable): 命令函数
            cmd (AvillaCommands): 命令对象
        """
        cmd.on(self.command, self.dispatchers, self.decorators, args=self.args, meta=self.meta)(func)  # type: ignore


class AvillaCommandsBehaviour(Behaviour):
    """命令行为"""

    def __init__(self, cmd: AvillaCommands) -> None:
        self.cmd = cmd

    def allocate(self, cube: Cube[Union[On, Command]]):
        if not isinstance(cube.metaclass, (On, Command)):
            return
        cube.metaclass.register(cube.content, self.cmd)
        return True

    def release(self, cube: Cube[Union[On, Command]]):
        if not isinstance(cube.metaclass, (On, Command)):
            return
        for key, target in self.cmd.trie.items():
            if TYPE_CHECKING:
                assert not isinstance(target, _NoChildren)

            if target[1].callable is cube.content:
                del self.cmd.trie[key]
                break

        return True

    uninstall = release
