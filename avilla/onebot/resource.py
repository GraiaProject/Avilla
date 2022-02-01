from typing import TYPE_CHECKING, Any

from avilla.core.context import ctx_avilla
from avilla.core.operator import OperatorCache, ResourceOperator
from avilla.core.selectors import resource as resource_selector
from avilla.core.service.entity import Status
from avilla.io.common.http import HttpClient

if TYPE_CHECKING:
    from .service import OnebotService


class OnebotImageAccessor(ResourceOperator):
    def __init__(self, service: "OnebotService", resource: resource_selector) -> None:
        self.service = service
        self.resource = resource

    async def operate(self, operator: str, target: Any, value: Any, cache: OperatorCache = None) -> Any:
        if operator == "read":
            url = self.resource.path["image"]
            avilla = self.service.protocol.avilla
            http_client = avilla.get_interface(HttpClient)
            async with http_client.get(url) as resp:
                resp.raise_for_status()
                stream = await resp.read()
                return Status(True, "success"), stream
        raise NotImplementedError(f"operator '{operator}' is not supported for image(onebot)")
