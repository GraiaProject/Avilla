from __future__ import annotations

import asyncio
import logging

from launart.manager import Launart
from launart.utilles import wait_fut
from loguru import logger
from uvicorn import Config, Server

from graia.amnesia.transport.common.asgi import AbstractAsgiService, ASGIHandlerProvider


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


class UvicornService(AbstractAsgiService):
    id = "http.asgi_runner/uvicorn"
    server: Server

    @property
    def required(self):
        return {ASGIHandlerProvider}

    @property
    def stages(self):
        return {"preparing", "cleanup"}

    async def launch(self, mgr: Launart):
        async with self.stage("preparing"):
            asgi_handler = mgr.get_interface(ASGIHandlerProvider).get_asgi_handler()
            self.server = WithoutSigHandlerServer(Config(asgi_handler, host=self.host, port=self.port))
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
            await wait_fut([serve_task, asyncio.sleep(10)], return_when=asyncio.FIRST_COMPLETED)
            if not serve_task.done():
                logger.warning("timeout, force exit uvicorn server...")
