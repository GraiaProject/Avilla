from typing import Any, Callable, Optional, TypeVar

from arclet.alconna import (
    Alconna,
    ArgsStub,
    Arparma,
    Duplication,
    OptionStub,
    SubcommandStub,
    command_manager,
    output_manager,
)
from arclet.alconna.argv import Argv, argv_config, set_default_argv_type
from arclet.alconna.builtin import generate_duplication
from creart import it
from pygtrie import CharTrie
from tarina import generic_issubclass, split_once
from tarina.generic import generic_isinstance, get_origin

from avilla.core import MessageReceived
from graia.amnesia.message import MessageChain
from graia.amnesia.message.element import Text
from graia.broadcast import Broadcast
from graia.broadcast.entities.dispatcher import BaseDispatcher
from graia.broadcast.interfaces.dispatcher import DispatcherInterface


class BaseMessageChainArgv(Argv[MessageChain]):
    @staticmethod
    def generate_token(data: list) -> int:
        return hash("".join(i.__repr__() for i in data))


set_default_argv_type(BaseMessageChainArgv)

argv_config(
    BaseMessageChainArgv,
    filter_out=[],
    checker=lambda x: isinstance(x, MessageChain),
    to_text=lambda x: x.text if isinstance(x, Text) else None,
    converter=lambda x: MessageChain(x if isinstance(x, list) else [Text(x)]),
)

TCallable = TypeVar("TCallable", bound=Callable[..., Any])


class AlconnaDispatcher(BaseDispatcher):
    def __init__(self, cmd: Alconna, arp: Arparma):
        super().__init__()
        self.cmd = cmd
        self.arp = arp

    async def catch(self, interface: DispatcherInterface):
        default_duplication = generate_duplication(self.cmd)(self.arp)
        if interface.annotation is Duplication:
            return default_duplication
        if generic_issubclass(Duplication, interface.annotation):
            return interface.annotation(self.arp)
        if interface.annotation is ArgsStub:
            arg = ArgsStub(self.cmd.args)
            arg.set_result(self.arp.all_matched_args)
            return arg
        if interface.annotation is OptionStub:
            return default_duplication.option(interface.name)
        if interface.annotation is SubcommandStub:
            return default_duplication.subcommand(interface.name)
        if generic_issubclass(get_origin(interface.annotation), Arparma):
            return self.arp
        if generic_issubclass(interface.annotation, Alconna):
            return self.cmd
        if interface.name in self.arp.all_matched_args:
            if generic_isinstance(self.arp.all_matched_args[interface.name], interface.annotation):
                return self.arp.all_matched_args[interface.name]
            return


class AvillaCommands:
    def __init__(self):
        self.trie: CharTrie = CharTrie()
        self.broadcast = it(Broadcast)

        @self.broadcast.receiver(MessageReceived)
        async def listener(event: MessageReceived):
            head, _ = split_once(str(event.message.content), (" ",))
            if target := self.trie.longest_prefix(head):
                await self.execute(target.value[0], target.value[1], event)  # type: ignore
            # shortcut
            for cmd in command_manager.get_commands():
                try:
                    command_manager.find_shortcut(cmd, head)
                except ValueError:
                    continue
                if target := self.trie.get(cmd.name):
                    await self.execute(target[0], target[1], event)
                    break

    def on(self, command: Alconna):
        if command.prefixes and not all(isinstance(i, str) for i in command.prefixes):
            raise TypeError("Command prefixes must be a list of string.")
        if not isinstance(command.command, str):
            raise TypeError("Command name must be a string.")

        def wrapper(func: Callable[..., Any]) -> Callable[..., Any]:
            if command.prefixes:
                for prefix in command.prefixes:
                    self.trie[prefix + command.name] = (command, func)
            else:
                self.trie[command.name] = (command, func)
            return func

        return wrapper

    async def execute(self, command: Alconna, func: Callable[..., Any], event: MessageReceived):
        with output_manager.capture(command.name) as cap:
            output_manager.set_action(lambda x: x, command.name)
            try:
                _res = command.parse(event.message.content)
            except Exception as e:
                _res = Arparma(command.path, event.message.content, False, error_info=e)
            may_help_text: Optional[str] = cap.get("output", None)
        if _res.matched:
            await self.broadcast.Executor(func, [event.Dispatcher, AlconnaDispatcher(command, _res)])
        elif may_help_text:
            await event.context.scene.send_message(may_help_text)


__all__ = ["AvillaCommands"]
