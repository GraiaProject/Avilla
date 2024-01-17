from __future__ import annotations

from collections import ChainMap
from contextlib import AsyncExitStack, ExitStack, asynccontextmanager, contextmanager
from typing import TYPE_CHECKING, Any, Callable, Generator, Generic, MutableSequence, overload
from typing_extensions import Concatenate

from ._runtime import AccessStack, GlobalArtifacts, Instances, Layout
from .fn.record import FnImplement
from .layout import DetailedArtifacts
from .topic import merge_topics_if_possible
from .typing import R1, P, Q, R, inTC
from .utils import standalone_context

if TYPE_CHECKING:
    from ._capability import CapabilityPerform
    from .fn import Fn
    from .fn.record import FnRecord
    from .perform import BasePerform


@standalone_context
def iter_artifacts(key: Any | None = None):
    collection = AccessStack.get(None)
    if collection is None:
        collection = {}
        AccessStack.set(collection)

    if key not in collection:
        stack = collection[key] = [-1]
    else:
        stack = collection[key]

    index = stack[-1]
    stack.append(index)

    start_offset = index + 1
    try:
        for stack[-1], content in enumerate(layout()[start_offset:], start=start_offset):
            yield content
    finally:
        stack.pop()
        if not stack:
            collection.pop(key, None)


def layout() -> MutableSequence[DetailedArtifacts[Any, Any]]:
    return Layout.get(None) or [GlobalArtifacts]


def shallow():
    return layout()[0]


def instances():
    return Instances.get()


@contextmanager
def provide(*instances_: Any):
    context_value = instances()
    if context_value is None:
        raise RuntimeError("provide() can only be used when instances available")

    old_values = {type_: context_value[type_] for instance in instances_ if (type_ := type(instance)) in context_value}

    context_value.update({type(instance): instance for instance in instances_})
    yield
    context_value.update(old_values)


def instance_of(cls: type):
    return instances()[cls]


@contextmanager
def using_sync(*performs: BasePerform):
    from .lifespan import AsyncLifespan, Lifespan

    with ExitStack() as stack:
        collection = [i.__collector__.artifacts for i in performs]

        for artifacts in collection:
            with isolate_layout():
                merge_topics_if_possible([artifacts], layout())

                if AsyncLifespan.compose_instance.signature() in artifacts:
                    raise RuntimeError("AsyncLifespan is not supported in sync_context()")

                if Lifespan.compose_instance.signature() in artifacts:
                    stack.enter_context(Lifespan.callee())

        stack.enter_context(isolate_layout())
        merge_topics_if_possible(collection, layout())

        stack.enter_context(isolate_instances())

        instance_record = instances()

        for instance in performs:
            instance_record[type(instance)] = instance

        yield stack


@asynccontextmanager
async def using_async(*performs: BasePerform):
    from .lifespan import AsyncLifespan, Lifespan

    async with AsyncExitStack() as stack:
        collections = [i.__collector__.artifacts for i in performs]

        for artifacts in collections:
            with isolate_layout():
                merge_topics_if_possible([artifacts], layout())

                if Lifespan.compose_instance.signature() in artifacts:
                    stack.enter_context(Lifespan.callee())

                if AsyncLifespan.compose_instance.signature() in artifacts:
                    await stack.enter_async_context(AsyncLifespan.callee())

        stack.enter_context(isolate_layout())
        merge_topics_if_possible(collections, layout())

        stack.enter_context(isolate_instances())
        instance_record = instances()

        for instance in performs:
            instance_record[type(instance)] = instance

        yield stack


class _WrapGenerator(Generic[R, Q, R1]):
    value: R1

    def __init__(self, gen: Generator[R, Q, R1]):
        self.gen = gen

    def __iter__(self) -> Generator[R, Q, R1]:
        self.value = yield from self.gen
        return self.value


def callee_of(target: Fn[Any, inTC] | FnImplement) -> inTC:
    from .fn import Fn
    from .fn.compose import EntitiesHarvest

    def wrapper(*args, **kwargs) -> Any:
        if isinstance(target, Fn):
            signature = target.compose_instance.signature()
        else:
            signature = target

        for artifacts in iter_artifacts(signature):
            if signature in artifacts:
                record: FnRecord = artifacts[signature]
                define = record["define"]

                wrap = _WrapGenerator(define.compose_instance.call(*args, **kwargs))

                for harvest_info in wrap:
                    scope = record["overload_scopes"][harvest_info.name]
                    stage = harvest_info.overload.harvest(scope, harvest_info.value)
                    endpoint = EntitiesHarvest.mutation_endpoint.get(None)
                    if endpoint is not None:
                        endpoint.commit(stage)

                return wrap.value
        else:
            raise NotImplementedError

    return wrapper  # type: ignore


@overload
def is_implemented(perform: type[BasePerform] | BasePerform, target: type[CapabilityPerform]) -> bool:
    ...


@overload
def is_implemented(perform: type[BasePerform] | BasePerform, target: Fn) -> bool:
    ...


@overload
def is_implemented(
    perform: type[BasePerform] | BasePerform,
    target: Fn[Callable[Concatenate[Any, P], Any], Any],
    *args: P.args,
    **kwargs: P.kwargs,
) -> bool:
    ...


def is_implemented(
    perform: type[BasePerform] | BasePerform, target: type[CapabilityPerform] | Fn, *args, **kwargs
) -> bool:
    if not isinstance(perform, type):
        perform = perform.__class__

    if isinstance(target, type):
        for define in target.__collector__.definations:
            if define.compose_instance.signature() in perform.__collector__.artifacts:
                return True
    else:
        fn_sign = target.compose_instance.signature()

        if fn_sign not in perform.__collector__.artifacts:
            return False

        if not (args or kwargs):
            return True

        record: FnRecord = perform.__collector__.artifacts[fn_sign]
        overload_scopes = record["overload_scopes"]

        slots = []

        for harvest_info in target.compose_instance.collect(Any, *args, **kwargs):
            sign = harvest_info.overload.digest(harvest_info.value)
            if harvest_info.name not in overload_scopes:
                return False
            scope = overload_scopes[harvest_info.name]
            twin_slot = harvest_info.overload.access(scope, sign)
            if twin_slot is None:
                return False
            slots.append(twin_slot)

        if slots and set(slots.pop()).intersection(*slots):
            return True

    return False


@contextmanager
def isolate_layout(backwards_protect: bool = True):
    upstream = layout()

    protected = []
    if backwards_protect:
        protected = [i for i in upstream if not i.protected]

    for protect_target in protected:
        protect_target.protected = True

    token = Layout.set([*upstream])
    try:
        yield
    finally:
        for i in protected:
            i.protected = False
        Layout.reset(token)


@contextmanager
def isolate_instances():
    token = Instances.set(ChainMap({}, *instances().maps))

    try:
        yield
    finally:
        Instances.reset(token)
