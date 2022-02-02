from typing import Final

from avilla.core.platform import Platform
from avilla.core.protocol import BaseProtocol


class ElizabethProtocol(BaseProtocol):
    platform: Final[Platform] = Platform(
        name="mirai-api-http for Avilla",
        protocol_provider_name="miraijvm-httpapi",
        implementation="avilla-elizabeth",
        supported_impl_version="v2",
        generation="v2",
    )
    required_components = {"http.universal_client"}
