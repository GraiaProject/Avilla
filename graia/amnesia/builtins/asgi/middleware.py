from __future__ import generator_stop

import functools
import inspect
import typing

import anyio
from asgiref import typing as asgitypes

MAX_QUEUE_SIZE = 10

T = typing.TypeVar("T")
U = typing.TypeVar("U")


class Left(typing.Generic[T, U]):
    def __init__(self, v: T):
        self.left = v


class Right(typing.Generic[T, U]):
    def __init__(self, v: U):
        self.right = v


Either = typing.Union[Left[T, U], Right[T, U]]


async def _invoke_asgi(
    app: asgitypes.ASGIApplication,
    scope: asgitypes.Scope,
    receive: asgitypes.ASGIReceiveCallable,
    send: asgitypes.ASGISendCallable,
) -> None:
    disambiguated = _disambiguate_app(app)
    if isinstance(disambiguated, Right):
        scope["asgi"]["version"] = "2.0"
        asgi_instance = disambiguated.right(scope)
        await asgi_instance(receive, send)
        return
    scope["asgi"]["version"] = "3.0"
    await disambiguated.left(scope, receive, send)


def _disambiguate_app(
    app: asgitypes.ASGIApplication,
) -> Either[asgitypes.ASGI3Application, asgitypes.ASGI2Application]:
    if inspect.isclass(app):
        return Right(typing.cast(asgitypes.ASGI2Application, app))

    if inspect.iscoroutinefunction(
        getattr(app, "__call__", None)
    ) or inspect.iscoroutinefunction(app):
        return Left(typing.cast(asgitypes.ASGI3Application, app))

    return Right(typing.cast(asgitypes.ASGI2Application, app))


class DispatcherMiddleware:
    def __init__(self, mounts: typing.Dict[str, asgitypes.ASGIApplication]) -> None:
        self.mounts = mounts

    async def __call__(
        self,
        scope: asgitypes.Scope,
        receive: asgitypes.ASGIReceiveCallable,
        send: asgitypes.ASGISendCallable,
    ) -> None:
        if scope["type"] == "lifespan":
            await self._handle_lifespan(scope, receive, send)
        else:
            for path, app in self.mounts.items():
                if scope["path"].startswith(path):
                    scope["path"] = scope["path"][len(path) :] or "/"  # type: ignore
                    return await _invoke_asgi(app, scope, receive, send)
            await send(
                asgitypes.HTTPResponseStartEvent(
                    type="http.response.start",
                    status=404,
                    headers=[(b"content-length", b"0")],
                    trailers=False,
                )
            )
            await send(
                asgitypes.HTTPResponseBodyEvent(
                    type="http.response.body", body=b"", more_body=False
                )
            )

    async def _handle_lifespan(
        self,
        scope: asgitypes.Scope,
        receive: asgitypes.ASGIReceiveCallable,
        send: asgitypes.ASGISendCallable,
    ) -> None:
        self.app_queues = {
            path: anyio.create_memory_object_stream(MAX_QUEUE_SIZE)
            for path in self.mounts
        }
        self.startup_complete = {path: False for path in self.mounts}
        self.shutdown_complete = {path: False for path in self.mounts}

        async with anyio.create_task_group() as tg:
            for path, app in self.mounts.items():
                await tg.spawn(
                    _invoke_asgi,
                    app,
                    scope,
                    self.app_queues[path][1].receive,
                    functools.partial(self.send, path, send),
                )

            while True:
                message = await receive()
                for channels in self.app_queues.values():
                    await channels[0].send(message)
                if message["type"] == "lifespan.shutdown":
                    break

    async def send(
        self,
        path: str,
        send: asgitypes.ASGISendCallable,
        message: asgitypes.ASGISendEvent,
    ) -> None:
        if message["type"] == "lifespan.startup.complete":
            self.startup_complete[path] = True
            if all(self.startup_complete.values()):
                await send(
                    asgitypes.LifespanStartupCompleteEvent(
                        type="lifespan.startup.complete"
                    )
                )
        elif message["type"] == "lifespan.shutdown.complete":
            self.shutdown_complete[path] = True
            if all(self.shutdown_complete.values()):
                await send(
                    asgitypes.LifespanShutdownCompleteEvent(
                        type="lifespan.shutdown.complete"
                    )
                )