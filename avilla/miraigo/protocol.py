from typing import Final, cast


from avilla.core.platform import Platform
from avilla.miraigo.event_parse import MiraigoEventParser
from avilla.miraigo.execution_ensure import MiraigoExecutionHandler
from avilla.miraigo.message_parse import MiraigoMessageParser
from avilla.miraigo.message_serialize import MiraigoMessageSerializer
from avilla.miraigo.service import MiraigoService
from avilla.onebot.event_parse import OnebotEventParser
from avilla.onebot.execution_ensure import OnebotExecutionHandler
from avilla.onebot.message_parse import OnebotMessageParser
from avilla.onebot.message_serialize import OnebotMessageSerializer
from avilla.onebot.protocol import OnebotProtocol
from avilla.onebot.service import OnebotService


class MiraigoProtocol(OnebotProtocol):
    platform: Final[Platform] = Platform(  # type: ignore
        name="Onebot v11 for Avilla, based on MiraiGo",
        protocol_provider_name="MiraiGo",
        implementation="avilla-onebot",
        supported_impl_version="1.0.0",
        generation="v11",
    )

    execution_handler: Final[OnebotExecutionHandler] = MiraigoExecutionHandler()  # type: ignore
    message_parser: Final[OnebotMessageParser] = MiraigoMessageParser()  # type: ignore
    message_serializer: Final[OnebotMessageSerializer] = MiraigoMessageSerializer()  # type: ignore
    event_parser: Final[OnebotEventParser] = MiraigoEventParser()  # type: ignore
    service: MiraigoService

    def __post_init__(self) -> None:
        if self.avilla.has_service(MiraigoService):
            self.service = self.avilla.get_service(MiraigoService)  # type: ignore
        else:
            self.service = MiraigoService(self)
            self.avilla.add_service(self.service)
