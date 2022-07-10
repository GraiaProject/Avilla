import sys

from creart import create
from graia.amnesia.builtins.aiohttp import AiohttpService
from graia.broadcast import Broadcast

from avilla.core import Avilla
from avilla.core.action import MessageSend
from avilla.core.event.message import MessageReceived
from avilla.core.relationship import Relationship
from avilla.elizabeth.protocol import ElizabethProtocol


def loguru_excepthook(ex_type, ex_value, ex_traceback):
    if ex_type is not None:
        import loguru

        loguru.logger.opt(exception=(ex_type, ex_value, ex_traceback)).error("Unhandled exception")
    else:
        import sys

        sys.__excepthook__(ex_type, ex_value, ex_traceback)


sys.excepthook = loguru_excepthook

protocol = ElizabethProtocol()
broadcast = create(Broadcast)
avilla = Avilla(broadcast, [protocol], [AiohttpService()])


@broadcast.receiver(MessageReceived)
async def on_message_received(event: MessageReceived):
    print(event.message)


avilla.launch_manager.launch_blocking(loop=broadcast.loop)
