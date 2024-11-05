from avilla.core import HttpRequestError
from avilla.telegram.exception import InvalidToken

code_exception_map: dict[int, type[Exception]] = {
    401: InvalidToken,
}


def validate_response(response: dict):
    if "ok" in response and response["ok"] is False:
        if response["error_code"] in code_exception_map:
            raise code_exception_map[response["error_code"]](response["description"])
        else:
            raise HttpRequestError(response["error_code"], response["description"])
