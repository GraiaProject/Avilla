from __future__ import annotations

import asyncio
import logging

from loguru import logger
from uvicorn import Config, Server

from launart import Launart, Launchable
from launart.utilles import any_completed

from .middleware import DispatcherMiddleware, asgitypes


class LoguruHandler(logging.Handler):
    def emit(self, record: logging.LogRecord) -> None:
        try:
            level = logger.level(record.levelname).name
        except ValueError:
            level = str(record.levelno)

        frame, depth = logging.currentframe(), 2
        while frame and frame.f_code.co_filename == logging.__file__:
            frame = frame.f_back
            depth += 1

        logger.opt(depth=depth, exception=record.exc_info).log(
            level,
            record.getMessage(),
        )


class WithoutSigHandlerServer(Server):
    def install_signal_handlers(self) -> None:
        pass


class UvicornASGIService(Launchable):
    id = "asgi.service/uvicorn"

    middleware: DispatcherMiddleware
    host: str
    port: int

    def __init__(
        self,
        host: str,
        port: int,
        mounts: dict[str, asgitypes.ASGIApplication] | None = None,
    ):
        self.host = host
        self.port = port
        self.middleware = DispatcherMiddleware(mounts or {})
        super().__init__()

    @property
    def required(self):
        return set()

    @property
    def stages(self):
        return {"preparing", "cleanup"}

    async def launch(self, manager: Launart) -> None:
        async with self.stage("preparing"):
            self.server = WithoutSigHandlerServer(Config(self.middleware, host=self.host, port=self.port))
            # TODO: 使用户拥有更多的对 Config 的配置能力.
    
            PATCHES = "uvicorn.error", "uvicorn.asgi", "uvicorn.access", ""
            level = logging.getLevelName(20)  # default level for uvicorn
            logging.basicConfig(handlers=[LoguruHandler()], level=level)

            for name in PATCHES:
                target = logging.getLogger(name)
                target.handlers = [LoguruHandler(level=level)]
                target.propagate = False

            serve_task = asyncio.create_task(self.server.serve())

        async with self.stage("cleanup"):
            logger.warning("try to shutdown uvicorn server...")
            self.server.should_exit = True
            await any_completed(serve_task, asyncio.sleep(10))
            if not serve_task.done():
                logger.warning("timeout, force exit uvicorn server...")
