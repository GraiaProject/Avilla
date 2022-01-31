from typing import TYPE_CHECKING, Any, Optional

from avilla.core.operator import MetadataOperator, OperatorCache
from avilla.core.selectors import entity as entity_selector
from avilla.core.selectors import mainline as mainline_selector
from avilla.core.utilles.operator import OperatorImplementDispatch
from avilla.onebot.operator_dispatch import OnebotOperatorDispatch

if TYPE_CHECKING:
    from avilla.onebot.protocol import OnebotProtocol


class OnebotOperator(MetadataOperator):
    protocol: "OnebotProtocol"
    account: entity_selector
    ctx: Optional[entity_selector] = None
    mainline: Optional[mainline_selector] = None

    def __init__(
        self,
        protocol: "OnebotProtocol",
        account: entity_selector,
        ctx: entity_selector = None,
        mainline: mainline_selector = None,
    ) -> None:
        self.protocol = protocol
        self.account = account
        self.ctx = ctx
        self.mainline = mainline

    operate_dispatch: "OperatorImplementDispatch[OnebotOperator]" = OnebotOperatorDispatch()

    async def operate(self, operator: str, target: Any, value: Any, cache: OperatorCache = None) -> Any:
        return await self.operate_dispatch.operate(self, operator, target, value, cache)
