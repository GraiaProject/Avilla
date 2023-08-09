from dataclasses import dataclass
from typing import (
    Any,
    Callable,
    Generic,
    Optional,
    TypeVar,
    Union,
    cast,
    get_args,
    overload,
)

from arclet.alconna import (
    Alconna,
    Arg,
    Args,
    ArgsStub,
    Arparma,
    CommandMeta,
    Duplication,
    Empty,
    OptionStub,
    SubcommandStub,
    command_manager,
    output_manager,
)
from arclet.alconna.args import TAValue
from arclet.alconna.argv import Argv, argv_config, set_default_argv_type
from arclet.alconna.builtin import generate_duplication
from arclet.alconna.tools.construct import _from_format as alconna_from_format
from creart import it
from graia.amnesia.message import MessageChain
from graia.amnesia.message.element import Text
from graia.broadcast import Broadcast
from graia.broadcast.entities.decorator import Decorator
from graia.broadcast.entities.dispatcher import BaseDispatcher
from graia.broadcast.entities.exectarget import ExecTarget
from graia.broadcast.interfaces.dispatcher import DispatcherInterface
from graia.broadcast.typing import T_Dispatcher
from nepattern import DirectPattern
from pygtrie import CharTrie
from tarina.generic import generic_isinstance, generic_issubclass, get_origin
from tarina.string import split_once

from avilla.core import MessageReceived

T = TypeVar("T")
TCallable = TypeVar("TCallable", bound=Callable[..., Any])


@dataclass
class Match(Generic[T]):
    """
    匹配项，表示参数是否存在于 `all_matched_args` 内

    result (T): 匹配结果

    available (bool): 匹配状态
    """

    result: T
    available: bool


class MessageChainArgv(Argv[MessageChain]):
    @staticmethod
    def generate_token(data: list) -> int:
        return hash("".join(i.__repr__() for i in data))


set_default_argv_type(MessageChainArgv)

argv_config(
    MessageChainArgv,
    filter_out=[],
    checker=lambda x: isinstance(x, MessageChain),
    to_text=lambda x: x.text if x.__class__ is Text else None,
    converter=lambda x: MessageChain(x if isinstance(x, list) else [Text(x)]),
)


@dataclass
class AlconnaDispatcher(BaseDispatcher):
    cmd: Alconna
    arp: Arparma

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
        if interface.annotation is Match:
            r = self.arp.all_matched_args.get(interface.name, Empty)
            return Match(r, r != Empty)
        if get_origin(interface.annotation) is Match:
            r = self.arp.all_matched_args.get(interface.name, Empty)
            return Match(r, generic_isinstance(r, get_args(interface.annotation)[0]))
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
            msg = str(event.message.content)
            if matches := self.trie.longest_prefix(msg):
                await self.execute(matches.value[0], matches.value[1], event)
                return
            # shortcut
            head, _ = split_once(msg, (" ",))
            for cmd, target in self.trie.values():
                try:
                    command_manager.find_shortcut(cmd, head)
                except ValueError:
                    continue
                await self.execute(cmd, target, event)

    @overload
    def on(
        self,
        command: Alconna,
        dispatchers: Optional[list[T_Dispatcher]] = None,
        decorators: Optional[list[Decorator]] = None,
    ) -> Callable[[TCallable], TCallable]:
        ...

    @overload
    def on(
        self,
        command: str,
        dispatchers: Optional[list[T_Dispatcher]] = None,
        decorators: Optional[list[Decorator]] = None,
        *,
        args: Optional[dict[str, Union[TAValue, Args, Arg]]] = None,
        meta: Optional[CommandMeta] = None,
    ) -> Callable[[TCallable], TCallable]:
        ...

    def on(
        self,
        command: Union[Alconna, str],
        dispatchers: Optional[list[T_Dispatcher]] = None,
        decorators: Optional[list[Decorator]] = None,
        *,
        args: Optional[dict[str, Union[TAValue, Args, Arg]]] = None,
        meta: Optional[CommandMeta] = None,
    ) -> Callable[[TCallable], TCallable]:
        def wrapper(func: TCallable) -> TCallable:
            target = ExecTarget(func, dispatchers, decorators)
            if isinstance(command, str):
                mapping = {arg.name: arg.value for arg in Args.from_callable(func)[0]}
                mapping.update(args or {})
                _command = alconna_from_format(command, mapping, meta)
                key = _command.name + "".join(
                    f" {arg.value.target}" for arg in _command.args if isinstance(arg.value, DirectPattern)
                )
                self.trie[key] = (_command, target)
            else:
                if not isinstance(command.command, str):
                    raise TypeError("Command name must be a string.")
                if not command.prefixes:
                    self.trie[command.command] = (command, target)
                elif not all(isinstance(i, str) for i in command.prefixes):
                    raise TypeError("Command prefixes must be a list of string.")
                else:
                    for prefix in cast(list[str], command.prefixes):
                        self.trie[prefix + command.command] = (command, target)
            return func

        return wrapper

    async def execute(self, command: Alconna, target: ExecTarget, event: MessageReceived):
        with output_manager.capture(command.name) as cap:
            output_manager.set_action(lambda x: x, command.name)
            try:
                _res = command.parse(event.message.content)
            except Exception as e:
                _res = Arparma(command.path, event.message.content, False, error_info=e)
            may_help_text: Optional[str] = cap.get("output", None)
        if _res.matched:
            await self.broadcast.Executor(target, [event.Dispatcher, AlconnaDispatcher(command, _res)])
        elif may_help_text:
            await event.context.scene.send_message(may_help_text)


__all__ = ["AvillaCommands", "Match"]
