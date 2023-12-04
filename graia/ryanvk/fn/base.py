from __future__ import annotations

from typing import TYPE_CHECKING, Any, Callable, Generic, Protocol, TypeVar

from typing_extensions import Concatenate

from ryanvk._runtime import upstream_staff
from ryanvk.entity import BaseEntity
from ryanvk.fn.compose import EntitiesHarvest, FnCompose
from ryanvk.fn.entity import FnImplementEntity
from ryanvk.fn.record import FnRecord
from ryanvk.typing import (
    FnComposeCallReturnType,
    FnComposeCollectReturnType,
    P,
    R,
    inTC,
    specifiedCollectP,
    unspecifiedCollectP,
)

if TYPE_CHECKING:
    from ryanvk.staff import Staff

K = TypeVar("K")

outboundShape = TypeVar("outboundShape", bound=Callable, covariant=True)


class FnMethodComposeCls(Protocol[P, R, unspecifiedCollectP]):
    def call(
        self,
        *args: P.args,
        **kwargs: P.kwargs,
    ) -> FnComposeCallReturnType[R]:
        ...

    def collect(
        self,
        *args: unspecifiedCollectP.args,
        **kwargs: unspecifiedCollectP.kwargs,
    ) -> FnComposeCollectReturnType:
        ...


class FnSymmetricCompose(Generic[P, R], FnCompose):
    def call(self, *args: P.args, **kwargs: P.kwargs) -> FnComposeCallReturnType[R]:
        with self.harvest() as entities:
            yield self.singleton.call(None)

        return entities.first(*args, **kwargs)

    def collect(self, implement: Callable[P, R]) -> FnComposeCollectReturnType:
        yield self.singleton.collect(None)


class Fn(Generic[unspecifiedCollectP, outboundShape], BaseEntity):
    compose_instance: FnCompose

    def __init__(self, compose_cls: type[FnCompose]):
        self.compose_instance = compose_cls(self)

    @classmethod
    def symmetric(cls: type[Fn[[Callable[P, R]], Callable[P, R]]], entity: Callable[Concatenate[Any, P], R]):
        return cls(FnSymmetricCompose[P, R])

    @classmethod
    def compose(
        cls: type[Fn[unspecifiedCollectP, Callable[P, R]]],
        compose_cls: type[FnMethodComposeCls[P, R, unspecifiedCollectP]],
    ):
        return cls(compose_cls)  # type: ignore

    @property
    def implements(
        self: Fn[Concatenate[Callable[P, R], specifiedCollectP], Any]
    ) -> Callable[
        specifiedCollectP,
        Callable[
            [Callable[Concatenate[K, P], R]],
            FnImplementEntity[Callable[Concatenate[K, P], R], specifiedCollectP],
        ],
    ]:
        def wrapper(*args: specifiedCollectP.args, **kwargs: specifiedCollectP.kwargs):
            def inner(
                impl: Callable[Concatenate[K, P], R]
            ) -> FnImplementEntity[Callable[Concatenate[K, P], R], specifiedCollectP]:
                return FnImplementEntity(self, impl, *args, **kwargs)

            return inner

        return wrapper  # type: ignore

    def call1(self: Fn[..., inTC], staff: Staff) -> inTC:
        def wrapper(*args, **kwargs):
            return self.call(staff, *args, **kwargs)

        return wrapper  # type: ignore

    def call(
        self: Fn[..., Callable[P, R]],
        staff: Staff,
        *args: P.args,
        **kwargs: P.kwargs,
    ) -> R:
        # FIXME: 用类似我在 entities.first 上的思路修复这个。
        #        我没头绪了……似乎比我想象中难了太多，如果要在一步，甚至就地/零步里完成这个的话。

        # FIXME: 什么时候去给 pyright 提个 issue 让 eric 彻底重构下现在 TypeVar binding 这坨狗屎。
        #
        #        无法将“type[str]”类型的参数分配给函数“call”中类型为“type[T@call]”的参数“value”
        #            无法将类型“type[str]”分配给类型“type[T@call]”
        #
        #        真是畜生啊。

        signature = self.compose_instance.signature()
        for artifacts in staff.iter_artifacts(signature):
            if signature in artifacts:
                record: FnRecord = artifacts[signature]
                define = record["define"]

                token = upstream_staff.set(staff)
                try:
                    iters = define.compose_instance.call(*args, **kwargs)
                    harvest_info = next(iters)
                    harv = EntitiesHarvest.mutation_endpoint.get()
                    while True:
                        scope = record["overload_scopes"][harvest_info.name]
                        stage = harvest_info.overload.harvest(scope, harvest_info.value)
                        harv.commit(stage)
                        harvest_info = next(iters)

                except StopIteration as e:
                    return e.value
                finally:
                    upstream_staff.reset(token)
        else:
            raise NotImplementedError
