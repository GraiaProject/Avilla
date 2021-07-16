# 首先, 先写个组合器, 可以同时 ws 和 http 那种.
import asyncio
import copy
from functools import reduce
from types import MappingProxyType
from typing import Generic, Type, TypeVar

from ..protocol import BaseProtocol

T_Protocol = TypeVar("T_Protocol", bound=BaseProtocol)


def compose_protocol(*protocols: Type[T_Protocol]) -> Type[T_Protocol]:
    result_proto = copy.copy(protocols[0])
    result_proto.ensureExecution.dispatcher.registry = MappingProxyType(
        reduce(
            lambda x, y: x | y,
            [dict(protocol.ensureExecution.dispatcher.registry) for protocol in protocols],
        )
    )

    async def fake_launch_entry(*args, **kwargs):
        return await asyncio.gather(*[protocol.launchEntry(*args, **kwargs) for protocol in protocols])

    result_proto.launchEntry = fake_launch_entry
    return result_proto
