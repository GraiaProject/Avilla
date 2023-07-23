import asyncio
import functools
import typing

import anyio
from asgiref import typing as asgitypes

MAX_QUEUE_SIZE = 10

T = typing.TypeVar("T")
U = typing.TypeVar("U")


class DispatcherMiddleware:
    def __init__(self, mounts: typing.Dict[str, asgitypes.ASGI3Application]) -> None:
        self.mounts = mounts

    async def __call__(self, scope: asgitypes.Scope, receive: typing.Callable, send: typing.Callable) -> None:
        if scope["type"] == "lifespan":
            await self._handle_lifespan(scope, receive, send)
        else:
            for path, app in self.mounts.items():
                if scope["path"].startswith(path):
                    scope["path"] = scope["path"][len(path) :] or "/"
                    return await app(scope, receive, send)

            if scope['type'] == "http":
                await send(
                    {
                        "type": "http.response.start",
                        "status": 404,
                        "headers": [(b"content-length", b"0")],
                    }
                )
                await send({"type": "http.response.body"})
            elif scope['type'] == "websocket":
                await send({
                    "type": "websocket.close"
                })

    async def _handle_lifespan(
        self,
        scope: asgitypes.Scope,
        receive: asgitypes.ASGIReceiveCallable,
        send: asgitypes.ASGISendCallable,
    ) -> None:
        self.app_queues = {path: asyncio.Queue(MAX_QUEUE_SIZE) for path in self.mounts}
        self.startup_complete = {path: False for path in self.mounts}
        self.shutdown_complete = {path: False for path in self.mounts}

        async with anyio.create_task_group() as tg:
            for path, app in self.mounts.items():
                await tg.spawn(
                    app,
                    scope,
                    self.app_queues[path].get,
                    functools.partial(self.send, path, send),
                )

            while True:
                message = await receive()
                for queue in self.app_queues.values():
                    await queue.put(message)
                if message["type"] == "lifespan.shutdown":
                    break

    async def send(self, path: str, send: typing.Callable, message: dict) -> None:
        if message["type"] == "lifespan.startup.complete":
            self.startup_complete[path] = True
            if all(self.startup_complete.values()):
                await send({"type": "lifespan.startup.complete"})
        elif message["type"] == "lifespan.shutdown.complete":
            self.shutdown_complete[path] = True
            if all(self.shutdown_complete.values()):
                await send({"type": "lifespan.shutdown.complete"})
