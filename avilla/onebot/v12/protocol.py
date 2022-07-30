from __future__ import annotations

from typing import ClassVar

from avilla.core.application import Avilla
from avilla.core.platform import Abstract, Land, Platform, Version
from avilla.core.protocol import BaseProtocol
from avilla.core.resource import PlatformResourceProvider
from avilla.core.utilles.metadata_source import ProtocolMetadataSource
from avilla.core.utilles.selector import Selector


class OneBot12Protocol(BaseProtocol):
    platform = Platform(
        Land(
            name="onebot",
            maintainers=[{"name": "GraiaProject"}],
            humanized_name="OneBot",
        ),
        Abstract(
            protocol="onebot",
            maintainers=[{"name": "howmanybots"}],
            humanized_name="OneBot",
        ),
        Version(
            {
                "onebot_spec": "v12",
            }
        ),
    )
