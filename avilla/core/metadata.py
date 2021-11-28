from datetime import datetime, timedelta
from typing import Dict, List, Tuple, Type, Union

from avilla.core.protocol import BaseProtocol

from .selectors import mainline, rsctx
from .utilles.selector import Selector

CONST_TYPES = Union[str, bool, int, float, datetime, timedelta]


class Metadata:
    scopes: Tuple[Type[Selector], ...]
    protocol: BaseProtocol

    def __init__(self, scopes: Tuple[Type[Selector], ...], protocol: BaseProtocol) -> None:
        self.scopes = scopes
        self.protocol = protocol

    async def check_operator(self, metakey: str, operator: str) -> bool:
        return any(
            [await self.protocol.check_metadata_access(scope, metakey, operator) for scope in self.scopes]
        )

    async def operate(
        self,
        scope: Union[Type[mainline], Type[rsctx]],
        metakey: str,
        operator: str,
        operator_value: Union[CONST_TYPES, List[CONST_TYPES], Dict[str, CONST_TYPES]],
    ) -> None:
        await self.protocol.operate_metadata(scope, metakey, operator, operator_value)


# rs.metadata.operate(metakey.scope['mainline'].id['group.name'], '=', 'group.name')
