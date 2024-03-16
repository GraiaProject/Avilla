from __future__ import annotations

from collections.abc import Mapping
from copy import copy, deepcopy
from typing import TYPE_CHECKING, Any, Awaitable, Callable, TypeVar, overload

from typing_extensions import Concatenate, ParamSpec, Self, Unpack

from avilla.core.metadata import Metadata, MetadataRoute
from avilla.core.ryanvk import Fn
from avilla.core.selector import EMPTY_MAP, Selector
from avilla.standard.core.privilege import Privilege
from avilla.standard.core.profile import Avatar, Nick, Summary

if TYPE_CHECKING:
    from . import Context

R = TypeVar("R", covariant=True)
P = ParamSpec("P")
_MetadataT = TypeVar("_MetadataT", bound=Metadata)


class ContextSelector(Selector):
    context: Context

    def __init__(self, cx: Context, pattern: Mapping[str, str] = EMPTY_MAP) -> None:
        super().__init__(pattern)
        self.context = cx

    def modify(self, pattern: Mapping[str, str]):
        return self.__class__(self.context, pattern)

    def __deepcopy__(self, memo):
        data = {**self.pattern}
        return self.__class__(copy(self.context), deepcopy(data, memo))

    @classmethod
    def from_selector(cls, cx: Context, selector: Selector) -> Self:
        return cls(cx, selector.pattern)

    @overload
    def __getitem__(self, item: str) -> str:
        ...

    @overload
    def __getitem__(self, item: Fn[Concatenate[Selector, P], R]) -> Callable[P, R]:
        ...

    def __getitem__(
        self,
        item: str | Fn[Concatenate[Selector, P], R],
    ) -> str | Callable[P, R]:
        if isinstance(item, str):
            return super().__getitem__(item)

        def wrapper(*args: P.args, **kwargs: P.kwargs) -> R:
            return self.context.staff.call_fn(item, self, *args, **kwargs)

        return wrapper

    def pull(
        self, metadata: type[_MetadataT] | MetadataRoute[Unpack[tuple[Any, ...]], _MetadataT]
    ) -> Awaitable[_MetadataT]:
        return self.context.pull(metadata, self)

    def nick(self):
        return self.pull(Nick)

    def summary(self):
        return self.pull(Summary)

    def avatar(self):
        return self.pull(Avatar)

    def privilege(self):
        return self.pull(Privilege)
