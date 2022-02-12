from avilla.core.exceptions import InvalidAuthentication, UnsupportedOperation


def raise_for_obresp(resp: dict):
    status = resp.get("status")
    if status != "ok":
        retcode = resp.get("retcode")
        if retcode == 401:
            raise InvalidAuthentication(resp)
        elif retcode == 403:
            raise InvalidAuthentication("Forbidden")
        elif retcode == 406:
            raise RuntimeError("not acceptable")
        elif retcode == 400:
            raise RuntimeError("not acceptable")
        elif retcode == 404:
            raise UnsupportedOperation("not found")
        elif retcode == 500:
            raise RuntimeError("internal server error")
        else:
            raise RuntimeError(f"Unknown error code: {retcode}")
