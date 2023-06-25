from typing import TYPE_CHECKING, Any, ChainMap, TypeVar

from typing_extensions import ParamSpec, Self

if TYPE_CHECKING:
    from .protocol import Executable

P = ParamSpec("P")
T = TypeVar("T", covariant=True)


class Runner:
    artifacts: ChainMap[Any, Any]

    def __init__(self):
        self.artifacts = ChainMap[Any, Any]()

    def execute(self, executable: Executable[Self, P, T], *args: P.args, **kwargs: P.kwargs) -> T:
        return executable.execute(self, *args, **kwargs)
