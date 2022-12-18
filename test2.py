from avilla.core.context import Context
from avilla.spec.core.message import MessageSend

a = Context()

a.wrap(MessageSend).send()

