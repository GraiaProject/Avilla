from __future__ import annotations

from asyncio import gather
from collections import ChainMap, deque
from collections.abc import AsyncGenerator, Awaitable, Callable, Iterable
from dataclasses import dataclass
from typing import TYPE_CHECKING, Any, TypeVar, cast, overload

from graia.amnesia.message import Element, MessageChain, Text
from typing_extensions import Self, Unpack

from avilla.core._runtime import ctx_context
from avilla.core.account import AbstractAccount
from avilla.core.message import Message
from avilla.core.metadata import Metadata, MetadataOf, MetadataRoute
from avilla.core.request import Request
from avilla.core.resource import Resource
from avilla.core.skeleton.message import MessageEdit, MessageRevoke, MessageSend
from avilla.core.skeleton.request import RequestTrait
from avilla.core.skeleton.scene import SceneTrait
from avilla.core.trait import Trait
from avilla.core.trait.context import GLOBAL_SCOPE, Scope
from avilla.core.trait.extension import ExtensionHandler
from avilla.core.trait.recorder import Querier
from avilla.core.trait.signature import (
    ArtifactSignature,
    CastAllow,
    Check,
    CompleteRule,
    Pull,
    Query,
    ResourceFetch,
)
from avilla.core.utilles import classproperty
from avilla.core.utilles.selector import MatchRule, Selectable, Selector

if TYPE_CHECKING:
    from avilla.core.protocol import BaseProtocol

_T = TypeVar("_T")
_MetadataT = TypeVar("_MetadataT", bound=Metadata)
_DescribeT = TypeVar("_DescribeT", bound=type[Metadata] | MetadataRoute)
_TraitT = TypeVar("_TraitT", bound=Trait)

_Describe = type[_MetadataT] | MetadataRoute[Unpack[tuple[Any, ...]], _MetadataT]


async def _query_depth_generator(
    rs: Context,
    current: Querier,
    predicate: Selector,
    upper_generator: AsyncGenerator[Selector, None] | None = None,
):
    if upper_generator is not None:
        async for i in upper_generator:
            async for j in current(rs, i, predicate):
                yield j
    else:
        async for j in current(rs, None, predicate):
            yield j


@dataclass
class _MatchStep:
    upper: str
    start: int
    history: tuple[Query, ...]


def _find_querier_steps(artifacts: ChainMap[ArtifactSignature, Any], query_path: str) -> list[Query] | None:
    result: list[Query] | None = None
    frags: list[str] = query_path.split(".")
    queue: deque[_MatchStep] = deque([_MatchStep("", 0, ())])
    while queue:
        head: _MatchStep = queue.popleft()
        current_steps: list[str] = []
        for curr_frag in frags[head.start :]:
            current_steps.append(curr_frag)
            steps = ".".join(current_steps)
            full_path = f"{head.upper}.{steps}" if head.upper else steps
            head.start += 1
            if (query := Query(head.upper or None, steps)) in artifacts:
                if full_path == query_path:
                    if result is None or len(result) > len(head.history) + 1:
                        result = [*head.history, query]
                else:
                    queue.append(
                        _MatchStep(
                            full_path,
                            head.start,
                            head.history + (query,),
                        )
                    )
    return result


class ContextSelector(Selector):
    context: Context

    def __init__(self, ctx: Context, *, mode: MatchRule = "exact", path_excludes: frozenset[str] = frozenset()) -> None:
        self.context = ctx
        super().__init__(mode=mode, path_excludes=path_excludes)

    @classmethod
    def from_selector(cls, ctx: Context, selector: Selector) -> Self:
        self = cls(ctx, mode=selector.mode, path_excludes=selector.path_excludes).set_referent(selector.referent)
        self.pattern = selector.pattern.copy()
        return self

    def pull(self, metadata: _Describe[_MetadataT]) -> Awaitable[_MetadataT]:
        return self.context.pull(metadata, self)

    def wrap(self, trait: type[_TraitT]) -> _TraitT:
        return self.context.wrap(self, trait)


class ContextClientSelector(ContextSelector):
    ...


class ContextEndpointSelector(ContextSelector):
    def expects_request(self) -> ContextRequestSelector:
        if "request" in self.pattern:
            return ContextRequestSelector.from_selector(self.context, self)

        raise ValueError(f"endpoint {self!r} is not a request endpoint")


class ContextSceneSelector(ContextSelector):
    def leave_scene(self):
        return self.wrap(SceneTrait).leave()

    def disband_scene(self):
        return self.wrap(SceneTrait).disband()

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
            reply = self.copy().message(reply)

        return self.wrap(MessageSend).send(message, reply=reply)

    def remove_member(self, target: Selector, reason: str | None = None):
        return self.wrap(SceneTrait).remove_member(target, reason)


class ContextRequestSelector(ContextEndpointSelector):
    def accept_request(self):
        return self.wrap(RequestTrait).accept()

    def reject_request(self, reason: str | None = None, forever: bool = False):
        return self.wrap(RequestTrait).reject(reason, forever)

    def cancel_request(self):
        return self.wrap(RequestTrait).cancel()

    def ignore_request(self):
        return self.wrap(RequestTrait).ignore()


@dataclass
class ContextMedium:
    selector: ContextSelector


@dataclass
class ContextWrappedMetadataOf(MetadataOf[_DescribeT]):
    ctx: Context

    def pull(self) -> Awaitable[_DescribeT]:
        return self.ctx.pull(self.describe, self.target)

    def wrap(self, trait: type[_TraitT]) -> _TraitT:
        return self.ctx.wrap(self, trait)


class Context:
    protocol: "BaseProtocol"
    account: AbstractAccount

    client: ContextClientSelector
    endpoint: ContextEndpointSelector
    scene: ContextSceneSelector
    self: Selector
    mediums: list[ContextMedium]

    cache: dict[str, Any]

    _artifacts: ChainMap[ArtifactSignature, Any]

    def __init__(
        self,
        protocol: "BaseProtocol",
        account: AbstractAccount,
        client: Selector,
        endpoint: Selector,
        scene: Selector,
        selft: Selector,
        mediums: list[Selector] | None = None,
        prelude_metadatas: dict[Selector | MetadataRoute, Metadata] | None = None,
    ) -> None:
        self.protocol = protocol
        self.account = account

        self.client = ContextClientSelector.from_selector(self, client)
        self.endpoint = ContextEndpointSelector.from_selector(self, endpoint)
        self.scene = ContextSceneSelector.from_selector(self, scene)
        self.self = selft
        self.mediums = [ContextMedium(ContextSelector.from_selector(self, medium)) for medium in mediums or []]

        self.cache = {"meta": prelude_metadatas or {}}

        self._artifacts = ChainMap(
            self.protocol.impl_namespace.get(
                Scope(self.land.name, self.scene.path_without_land, self.self.path_without_land), {}
            ),
            self.protocol.impl_namespace.get(Scope(self.land.name, self.scene.path_without_land), {}),
            self.protocol.impl_namespace.get(Scope(self.land.name, self=self.self.path_without_land), {}),
            self.protocol.impl_namespace.get(Scope(self.land.name), {}),
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
    def _ext_handler(self):
        return ExtensionHandler(self)

    @classproperty
    @classmethod
    def app_current(cls) -> Context | None:
        return ctx_context.get(None)

    @property
    def request(self) -> ContextRequestSelector:
        return self.endpoint.expects_request()

    async def query(self, pattern: Selector, with_land: bool = False):
        querier_steps: list[Query] | None = _find_querier_steps(
            self._artifacts, pattern.path if with_land else pattern.path_without_land
        )

        if querier_steps is None:
            raise NotImplementedError(f'cannot query "{pattern.path_without_land}" due to unknown step calc.')

        querier = cast("dict[Query, Querier]", {i: self._artifacts[i] for i in querier_steps})
        generators: list[AsyncGenerator[Selector, None]] = []

        past = []
        for k, v in querier.items():
            past.append(k.target)
            pred = pattern.mixin(".".join(past))
            current = _query_depth_generator(self, v, pred, generators[-1] if generators else None)
            generators.append(current)

        async for i in generators[-1]:
            if with_land:
                yield Selector.from_dict({"land": self.land.name, **i.pattern})
            else:
                yield i

    @overload
    async def check(self, *, check_via: bool = True) -> None:
        # 检查 Relationship 的存在性。
        # 如 Relationship 的存在性无法被验证为真，则 Relationship 不成立，抛出错误。
        ...

    @overload
    async def check(self, target: Selector, *, strict: bool = False, check_via: bool = True) -> bool:
        # 检查 target 相对于当前关系 Relationship 的存在性。
        # 注意，这里是 "相对于当前关系", 如 Github 的项目若为 Private, 则对于外界/Amonymous来说是不存在的, 即使他从客观上是存在的。
        # 注意，target 不仅需要相对于当前关系是存在的，由于关系本身处在一个 mainline 之中，
        # mainline 相当于工作目录或者是 docker 那样的应用容器，后者是更严谨的比喻，
        # 因为有些操作**只能**在处于一个特定的 mainline 中才能完成，这其中包含了访问并操作某些 target.
        # 在 strict 模式下，target 被视作包含 "仅在当前 mainline 中才能完成的操作" 的集合中，
        # 表示其访问或是操作必须以当前 mainline 甚至是 current(account) 为基础。
        # 如果存在可能的 via, 则会先检查 via 的存在性，因为 via 是维系这段关系的基础。
        ...

    async def check(
        self, target: Selector | None = None, *, strict: bool = False, check_via: bool = True
    ) -> bool | None:
        # FIXME: check this sentence again
        if check_via and self.mediums is not None:
            await gather(*(self.check(medium.selector, strict=True, check_via=False) for medium in self.mediums))
        checker = self._artifacts.get(Check((target or self.endpoint).path_without_land))
        if checker is None:
            raise NotImplementedError(
                f'cannot check existence & accessible of "{(target or self.endpoint).path_without_land}" due to notimplemented checker'
            )
        result = checker(self, target)
        if strict and not result:
            raise ValueError(f"check failed on {target or self.endpoint!r}")
        return result

    def complete(self, selector: Selector, with_land: bool = False):
        output_rule = self._artifacts.get(CompleteRule(selector.path_without_land))
        if output_rule is not None:
            output_rule = cast(str, output_rule)
            selector = Selector().mixin(output_rule, selector, self.endpoint, self.scene)
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
        path: type[_MetadataT] | MetadataRoute[Unpack[tuple[Any, ...]], _MetadataT],
        target: Selector | Selectable | None = None,
        *,
        flush: bool = False,
    ) -> _MetadataT:
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
        puller = cast("Callable[[Context, Selector | None], Awaitable[_MetadataT]]", puller)
        result = await puller(self, target)
        if target is not None and not path.has_params():
            cached = self.cache["meta"].setdefault(target, {})
            cached[path] = result
        return result

    @overload
    def wrap(self, bound: Selector) -> ContextSelector:
        ...

    @overload
    def wrap(self, bound: MetadataOf[_Describe]) -> ContextWrappedMetadataOf[_Describe]:
        ...

    @overload
    def wrap(self, bound: Selector, trait: type[_TraitT]) -> _TraitT:
        ...

    @overload
    def wrap(self, bound: MetadataOf, trait: type[_TraitT]) -> _TraitT:
        ...

    def wrap(
        self,
        bound: Selector | MetadataOf[_DescribeT],
        trait: type[_TraitT] | None = None,
    ) -> ContextSelector | ContextWrappedMetadataOf[_Describe] | _TraitT:
        if trait:
            if CastAllow(trait) not in self._artifacts:
                raise NotImplementedError(f"trait {trait.__name__} is not allow to cast in current context.")

            if isinstance(bound, Selector):
                return trait(self, None, bound)
            elif isinstance(bound, MetadataOf):
                return trait(self, bound.describe, bound.target)

        elif isinstance(bound, Selector):
            return ContextSelector.from_selector(self, bound)
        elif isinstance(bound, MetadataOf):
            return ContextWrappedMetadataOf(bound.target, bound.describe, self)

        raise TypeError(f"cannot wrap {bound!r}")
