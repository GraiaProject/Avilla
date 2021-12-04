from asyncio.coroutines import iscoroutine
from typing import Any, Callable, Iterable, Optional
from prompt_toolkit import PromptSession
from prompt_toolkit.patch_stdout import StdoutProxy
import asyncio


class RichStdoutProxy(StdoutProxy):
    "StdoutProxy with writelines support for Rich."

    def writelines(self, data: Iterable[str]) -> None:
        with self._lock:
            for d in data:
                self._write(d)


class AvillaConsole:
    def __init__(self, callback: Optional[Callable[[str], Any]] = None) -> None:
        self.session = PromptSession()
        self.task = None
        self.callback = callback
        self.running = False

    async def read(self):
        while self.running:
            string: str = await self.session.prompt_async("Avilla > ")
            if self.callback:
                r = self.callback(string)
                if iscoroutine(r):
                    await r

    async def start(self):
        if not self.running:
            self.running = True
            self.task = asyncio.create_task(self.read())

    def stop(self):
        self.running = False


AVILLA_ASCII_LOGO = r""" Avilla - The next-gen framework for IM development.
    _        _ _ _
   / \__   _(_) | | __ _
  / _ \ \ / / | | |/ _` |
 / ___ \ V /| | | | (_| |
/_/   \_\_/ |_|_|_|\__,_|"""

if __name__ == "__main__":
    from loguru import logger
    from rich.console import Console
    from rich.logging import RichHandler
    from prompt_toolkit.patch_stdout import StdoutProxy

    console = Console(file=RichStdoutProxy(raw=True))  # type: ignore

    logger.configure(
        handlers=[
            {
                "sink": RichHandler(console=console, markup=True),
                "format": "<green>{time:YYYY-MM-DD HH:mm:ss.SSS}</green> | <level>{level: <8}</level> | "
                "<cyan>{name}</cyan>: <cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>",
            }
        ]
    )
    logger.opt(raw=True).info(AVILLA_ASCII_LOGO)

    async def cb(s: str):
        if s.startswith(".stop"):
            con.stop()
        else:
            logger.info(f"You typed: [b green]{s}[/]")

    con = AvillaConsole(cb)

    async def main():
        await con.start()
        while con.running:
            await asyncio.sleep(0.5)
            logger.info("[b red]test[/]ing...")

    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        pass
