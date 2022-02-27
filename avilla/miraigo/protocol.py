from typing import Final

from avilla.core.platform import Adapter, Base, Medium, Platform
from avilla.miraigo.event_parse import MiraigoEventParser
from avilla.miraigo.execution_ensure import MiraigoExecutionHandler
from avilla.miraigo.message_parse import MiraigoMessageParser
from avilla.miraigo.message_serialize import MiraigoMessageSerializer
from avilla.miraigo.service import MiraigoService
from avilla.onebot.protocol import OnebotProtocol


class MiraigoProtocol(OnebotProtocol):
    platform: Final[Platform] = Platform(  # type: ignore
        Base(supplier="Tencent", name="qq", humanized_name="QQ"),
        Medium(
            supplier="Mrs4s@github",
            name="miraigo",
            humanized_name="MiraiGo",
            generation="v11",
            version="1.0.0",
        ),
        Adapter(
            supplier="GraiaProject@github",
            name="miraigo-protocol",
            humanized_name="OneBot for Avilla, based on MiraiGo",
            version="unknown",
        ),
    )

    execution_handler: Final[MiraigoExecutionHandler] = MiraigoExecutionHandler()  # type: ignore
    message_parser: Final[MiraigoMessageParser] = MiraigoMessageParser()  # type: ignore
    message_serializer: Final[MiraigoMessageSerializer] = MiraigoMessageSerializer()  # type: ignore
    event_parser: Final[MiraigoEventParser] = MiraigoEventParser()  # type: ignore
    service: MiraigoService

    def __post_init__(self) -> None:
        if self.avilla.has_service(MiraigoService):
            self.service = self.avilla.get_service(MiraigoService)  # type: ignore
        else:
            self.service = MiraigoService(self)
            self.avilla.add_service(self.service)
