from typing import Final

from avilla.core.platform import Adapter, Base, Medium, Platform
from avilla.core.protocol import BaseProtocol


class ElizabethProtocol(BaseProtocol):
    platform: Final[Platform] = Platform(  # type: ignore
        Base(supplier="Tencent", name="qq", humanized_name="QQ"),
        Medium(
            supplier="project-mirai@github",
            name="miraijvm-httpapi",
            humanized_name="mirai-api-http",
            generation="v2",
            version="unknown"
        ),
        Adapter(
            supplier="GraiaProject@github",
            name="elizabeth-protocol",
            humanized_name="mirai-api-http for Avilla",
            version="unknown",
        )
    )
    required_components = {"http.universal_client"}
