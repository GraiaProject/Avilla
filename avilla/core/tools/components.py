from typing import Callable, Generic, Optional, Tuple, Type, TypeVar, Union

from graia.broadcast.entities.decorator import Decorator
from graia.broadcast.interfaces.decorator import DecoratorInterface

from avilla.core.message import Element, MessageChain

T = TypeVar("T")


class Components(Decorator, Generic[T]):
    _filter: Callable[[Element], bool]
    _match_times: Optional[int] = None
    _skip_times: int = 0

    def __init__(
        self,
        filter_callable: Callable[[Element], bool],
        match_times: Optional[int] = None,
        skip_times: int = 0,
    ) -> None:
        self._filter = filter_callable
        self._match_times = match_times
        self._skip_times = skip_times

    @classmethod
    def __class_getitem__(cls, item: Union[Type[Element], Tuple[Type[Element], ...], slice]) -> "Components":
        element_type: Union[Type[Element], Tuple[Type[Element], ...]] = Element
        match_times = None
        if isinstance(item, slice):
            if item.stop <= 0:
                raise TypeError("you should put a positive number.")
            element_type, match_times = item.start, item.stop
        else:  # 因为是用的 isinstance 判断, 所以问题不大(isinstance 第二个参数允许是 tuple.)
            if isinstance(item, list):
                item = tuple(item)
            element_type = item

        def matcher(element: Element):
            return isinstance(element, element_type)

        return cls(matcher, match_times)

    async def target(self, interface: DecoratorInterface):
        chain: MessageChain
        if interface.annotation != MessageChain:
            chain = await interface.dispatcher_interface.lookup_param("message", MessageChain, None)
        else:
            chain = interface.return_value

        selected = []
        matched_times = 0
        for value in chain.content:
            if self._match_times is not None:
                if matched_times >= self._match_times + self._skip_times:
                    break
            if self._filter(value):
                selected.append(value)
                matched_times += 1

        return MessageChain(selected[self._skip_times :])
