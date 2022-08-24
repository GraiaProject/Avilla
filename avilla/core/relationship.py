from __future__ import annotations

from collections import ChainMap, defaultdict
from typing import (
    TYPE_CHECKING,
    Any,
    AsyncGenerator,
    Awaitable,
    Callable,
    Iterable,
    TypeVar,
    cast,
    overload,
)

from graia.amnesia.message import Element, MessageChain, Text
from typing_extensions import Unpack

from avilla.core.account import AbstractAccount

# from avilla.core.action.middleware import ActionMiddleware
from avilla.core.cell import Cell, CellOf
from avilla.core.context import ctx_relationship
from avilla.core.message import Message
from avilla.core.request import Request
from avilla.core.resource import Resource
from avilla.core.skeleton.message import MessageTrait
from avilla.core.skeleton.request import RequestTrait
from avilla.core.skeleton.scene import SceneTrait
from avilla.core.traitof import Trait
from avilla.core.traitof.context import GLOBAL_SCOPE, Scope
from avilla.core.traitof.recorder import Querier
from avilla.core.traitof.signature import (
    ArtifactSignature,
    CompleteRule,
    Pull,
    Query,
    ResourceFetch,
)
from avilla.core.utilles.selector import Selectable, Selector

if TYPE_CHECKING:
    from avilla.core.protocol import BaseProtocol

_T = TypeVar("_T")
_M = TypeVar("_M", bound=Cell)
_TboundTrait = TypeVar("_TboundTrait", bound=Trait)

async def _query_depth_generator(current: Querier, predicate: Selector, upper_generator: AsyncGenerator[Selector, None] | None = None):
    if upper_generator is not None:
        async for i in upper_generator:
            async for j in current(i, predicate):
                yield j
    else:
        async for j in current(None, predicate):
            yield j
class Relationship:
    ctx: Selector
    mainline: Selector
    self: Selector
    via: Selector | None = None

    account: AbstractAccount
    cache: dict[str, Any]

    protocol: "BaseProtocol"

    _artifacts: ChainMap[ArtifactSignature, Any]
    # _middlewares: list[ActionMiddleware]

    def __init__(
        self,
        protocol: "BaseProtocol",
        ctx: Selector,
        mainline: Selector,
        selft: Selector,
        account: AbstractAccount,
        via: Selector | None = None,
        # middlewares: list[ActionMiddleware] | None = None,
    ) -> None:
        self.ctx = ctx
        self.mainline = mainline
        self.self = selft
        self.via = via
        self.account = account
        self.protocol = protocol
        # self._middlewares = middlewares or []
        self.cache = {"meta": {}}
        self._artifacts = ChainMap(
            self.protocol.impl_namespace.get(Scope(self.mainline.path_without_land, self.self.path_without_land), {}),
            self.protocol.impl_namespace.get(Scope(self.mainline.path_without_land), {}),
            self.protocol.impl_namespace.get(Scope(self=self.self.path_without_land), {}),
            self.protocol.impl_namespace.get(GLOBAL_SCOPE, {}),
            self.avilla.global_artifacts,
        )

    @property
    def avilla(self):
        return self.protocol.avilla

    @property
    def land(self):
        return self.protocol.land

    @property
    def is_resource(self) -> bool:
        # TODO: Auto inference for implementations of a "ctx"
        ...

    @property
    def app_current(self) -> Relationship | None:
        return ctx_relationship.get(None)

    async def query(self, pattern: Selector):
        querier_steps: list[Query] | None = None

        query_map: defaultdict[str | None, dict[str, Any]] = defaultdict(dict)
        query_path: str = pattern.path_without_land
        candidates: dict[str, list[Query]] = {}

        for k, v in self._artifacts.items():
            if isinstance(k, Query):
                if k.upper is None:
                    if k.target == query_path:
                        if querier_steps is None or 1 < len(querier_steps):
                            querier_steps = [k]
                    else:
                        candidates[k.target] = [k]
                query_map[k.upper][k.target] = v

        while candidates:
            nxt: dict[str, list[Query]] = {}
            for upper, query_list in candidates.items():
                for path_frag in query_map[upper]:
                    nxt_frag = f"{upper}.{path_frag}"
                    if nxt_frag not in query_path:
                        continue
                    nxt_query_list = query_list + [Query(upper, path_frag)]
                    if nxt_frag == query_path:
                        if querier_steps is None or len(nxt_query_list) < len(querier_steps):
                            querier_steps: list[Query] | None = nxt_query_list
                    else:
                        if nxt_frag not in nxt or len(nxt_query_list) < len(nxt[nxt_frag]):
                            nxt[nxt_frag] = nxt_query_list
            candidates = nxt
        
        if querier_steps is None:
            raise NotImplementedError # TODO: error message

        querier = cast("dict[str, Querier]", {i.target: self._artifacts[i] for i in querier_steps})
        generators: list[AsyncGenerator[Selector, None]] = []
        
        upper_generator: AsyncGenerator[Selector, None] | None = None
        for k, v in querier.items():
            pred = pattern.mixin(k)
            current = _query_depth_generator(v, pred, upper_generator)
            generators.append(current)
            upper_generator = current
            
        async for i in generators[-1]:
            yield i

    @overload
    async def check(self) -> None:
        # 检查 Relationship 的存在性.
        # 如 Relationship 的存在性无法被验证为真, 则 Relationship 不成立, 抛出错误.
        ...

    @overload
    async def check(self, target: Selector, strict: bool = False) -> bool:
        # 检查 target 相对于当前关系 Relationship 的存在性.
        # 注意, 这里是 "相对于当前关系", 如 Github 的项目若为 Private, 则对于外界/Amonymous来说是不存在的, 即使他从客观上是存在的.
        # 注意, target 不仅需要相对于当前关系是存在的, 由于关系本身处在一个 mainline 之中,
        # mainline 相当于工作目录或者是 docker 那样的应用容器, 后者是更严谨的比喻,
        # 因为有些操作**只能**在处于一个特定的 mainline 中才能完成, 这其中包含了访问并操作某些 target.
        # 在 strict 模式下, target 被视作包含 "仅在当前 mainline 中才能完成的操作" 的集合中,
        # 表示其访问或是操作必须以当前 mainline 甚至是 current(account) 为基础.
        # 如果存在可能的 via, 则会先检查 via 的存在性, 因为 via 是维系这段关系的基础.
        ...

    async def check(self, target: Selector | None = None, strict: bool = False) -> bool | None:
        ...

    def complete(self, selector: Selector, with_land: bool = False):
        output_rule = self._artifacts.get(CompleteRule(selector.path_without_land))
        if output_rule is not None:
            output_rule = cast(str, output_rule)
            selector = Selector().mixin(output_rule, selector, self.ctx, self.mainline)
        if with_land and list(selector.pattern.keys())[0] != "land":
            selector.pattern = {"land": self.land.name, **selector.pattern}
        return selector

    async def fetch(self, resource: Resource[_T]) -> _T:
        fetcher = self._artifacts.get(ResourceFetch(type(resource)))
        if fetcher is None:
            raise NotImplementedError(
                f'cannot fetch "{resource.selector}" '
                + f' because no available fetch implement found in "{self.protocol.__class__.__name__}"'
            )
        return await fetcher(self, resource)

    async def pull(
        self,
        path: type[_M] | CellOf[Unpack[tuple[Any, ...]], _M],
        target: Selector | Selectable | None = None,
        *,
        flush: bool = False,
    ) -> _M:
        if isinstance(target, Selectable):
            target = target.to_selector()
        if target is not None:
            cached = self.cache["meta"].get(target)
            if cached is not None and path in cached:
                if flush:
                    del cached[path]
                elif not path.has_params():
                    return cached[path]

        puller = self._artifacts.get(Pull(target.path_without_land if target is not None else None, path))
        if puller is None:
            raise NotImplementedError(
                f'cannot pull "{path}"'
                + (f' for "{target.path_without_land}"' if target is not None else "")
                + f' because no available implement found in "{self.protocol.__class__.__name__}"'
            )
        puller = cast("Callable[[Relationship, Selector | None], Awaitable[_M]]", puller)
        result = await puller(self, target)
        if target is not None and not path.has_params():
            cached = self.cache["meta"].setdefault(target, {})
            cached[path] = result
        return result

    def cast(
        self,
        trait: type[_TboundTrait],
        path: type[Cell] | CellOf[Unpack[tuple[Any, ...]], Cell] | None = None,
        target: Selector | Selectable | None = None,
    ) -> _TboundTrait:
        if isinstance(target, Selectable):
            target = target.to_selector()
        return trait(self, path, target)

    def send_message(
        self, message: MessageChain | str | Iterable[str | Element], *, reply: Message | Selector | str | None = None
    ):
        if isinstance(message, str):
            message = MessageChain([Text(message)])
        elif not isinstance(message, MessageChain):
            message = MessageChain([]).extend(list(message))
        else:
            message = MessageChain([i if isinstance(i, Element) else Text(i) for i in message])

        if isinstance(reply, Message):
            reply = reply.to_selector()
        elif isinstance(reply, str):
            reply = self.mainline.copy().message(reply)

        return self.cast(MessageTrait).send(message, reply=reply)

    # TODO: more shortcuts, like `accept_request` etc.

    async def accept_request(self, request: Request | Selector):
        if isinstance(request, Request):
            request = request.to_selector()
        return await self.cast(RequestTrait, target=request).accept()

    async def reject_request(self, request: Request | Selector, reason: str | None = None, forever: bool = False):
        if isinstance(request, Request):
            request = request.to_selector()
        return await self.cast(RequestTrait, target=request).reject(reason, forever)

    async def cancel_request(self, request: Request | Selector):
        if isinstance(request, Request):
            request = request.to_selector()
        return await self.cast(RequestTrait, target=request).cancel()

    async def ignore_request(self, request: Request | Selector):
        if isinstance(request, Request):
            request = request.to_selector()
        return await self.cast(RequestTrait, target=request).ignore()

    async def leave_scene(self, scene: Selectable | Selector | None = None):
        if isinstance(scene, Selectable):
            scene = scene.to_selector()
        return await self.cast(SceneTrait, target=scene or self.mainline).leave()

    async def disband_scene(self, scene: Selectable | Selector | None = None):
        if isinstance(scene, Selectable):
            scene = scene.to_selector()
        return await self.cast(SceneTrait, target=scene or self.mainline).disband()

    async def remove_member(
        self, target: Selector, reason: str | None = None, scene: Selectable | Selector | None = None
    ):
        if isinstance(scene, Selectable):
            scene = scene.to_selector()
        return await self.cast(SceneTrait, target=scene or self.mainline).remove_member(target, reason)
