from typing import Any, Callable
from prompt_toolkit import PromptSession


class AvillaConsole:
    def __init__(self, callback: Callable[[str], Any]) -> None:
        self.session = PromptSession()
        self.task = None
        self.callback = callback
        self.running = False

    async def read(self):
        while self.running:
            string: str = await self.session.prompt_async("Avilla > ")
            await self.callback(string)

    async def start(self):
        if not self.running:
            self.running = True
            await self.read()

    def stop(self):
        self.running = False
