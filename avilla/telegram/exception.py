from avilla.core import InvalidAuthentication, InvalidOperation


class InvalidToken(InvalidAuthentication):
    pass


class InvalidEditedMessage(InvalidOperation):
    pass
