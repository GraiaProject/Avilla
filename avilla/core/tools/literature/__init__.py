import getopt
import itertools
import re
import shlex
from typing import Dict, List, Sequence

from graia.broadcast.entities.dispatcher import BaseDispatcher
from graia.broadcast.entities.signatures import Force
from graia.broadcast.exceptions import ExecutionStop
from graia.broadcast.interfaces.dispatcher import DispatcherInterface

from avilla.core.builtins.elements import Text
from avilla.core.message.chain import MessageChain
from avilla.core.message.element import Element

from .pattern import BoxParameter, ParamPattern, SwitchParameter

BLOCKING_ELEMENTS = ()


class Literature(BaseDispatcher):
    """旅途的浪漫
    Avilla Migrated> 如果使用中发现任何属因移植过程发生的错误, 提交 issue.
    """

    always = False
    prefixs: Sequence[str]  # 匹配前缀
    arguments: Dict[str, ParamPattern]

    allow_quote: bool
    skip_one_at_in_quote: bool

    def __init__(
        self,
        *prefixs: str,
        arguments: Dict[str, ParamPattern] = None,
        allow_quote: bool = False,
        skip_one_at_in_quote: bool = False,
    ) -> None:
        self.prefixs = prefixs
        self.arguments = arguments or {}
        self.allow_quote = allow_quote
        self.skip_one_at_in_quote = skip_one_at_in_quote

    def trans_to_map(self, message_chain: MessageChain):
        string_result: List[str] = []
        id_elem_map: Dict[int, Element] = {}

        for elem in message_chain.__root__:
            if isinstance(elem, Text):
                string_result.append(
                    re.sub(
                        r"\$(?P<id>\d+)",
                        lambda match: f'\\${match.group("id")}',
                        elem.text,
                    )
                )
            else:
                index = len(id_elem_map) + 1
                string_result.append(f"${index}")
                id_elem_map[index] = elem

        return ("".join(string_result), id_elem_map)

    def gen_long_map(self):
        result = {}
        for param_name, arg in self.arguments.items():
            for long in arg.longs:
                if long in result:
                    raise ValueError("conflict item")
                result[long] = param_name
        return result

    def gen_short_map(self):
        result = {}
        for param_name, arg in self.arguments.items():
            if arg.short in result:
                raise ValueError("conflict item")
            result[arg.short] = param_name
        return result

    def gen_long_map_with_bar(self):
        return {("--" + k): v for k, v in self.gen_long_map().items()}

    def gen_short_map_with_bar(self):
        return {("-" + k): v for k, v in self.gen_short_map().items() if k is not None}

    def parse_message(self, message_chain: MessageChain):
        string_result, id_elem_map = self.trans_to_map(message_chain)

        parsed_args, variables = getopt.getopt(
            shlex.split(string_result),
            "".join(
                [
                    arg.short if isinstance(arg, SwitchParameter) else (arg.short + ":")
                    for arg in self.arguments.values()
                    if arg.short
                ]
            ),
            [
                long if isinstance(arg, SwitchParameter) else long + "="
                for arg in self.arguments.values()
                for long in arg.longs
            ],
        )
        map_with_bar = {**self.gen_long_map_with_bar(), **self.gen_short_map_with_bar()}
        parsed_args = {
            map_with_bar[k]: (
                MessageChain.create(
                    [
                        Text(i) if not re.match(r"^\$\d+$", i) else id_elem_map[int(i[1:])]
                        for i in re.split(r"((?<!\\)\$[0-9]+)", v)
                        if i
                    ]
                ).as_merged()
                if isinstance(self.arguments[map_with_bar[k]], BoxParameter)
                else (
                    self.arguments[map_with_bar[k]].auto_reverse  # type: ignore
                    and not self.arguments[map_with_bar[k]].default
                    or True
                ),
                self.arguments[map_with_bar[k]],
            )
            for k, v in parsed_args
        }
        variables = [
            MessageChain.create(
                [
                    Text(i) if not re.match(r"^\$\d+$", i) else id_elem_map[int(i[1:])]
                    for i in re.split(r"((?<!\\)\$[0-9]+)", v)
                    if i
                ]
            ).as_merged()
            for v in variables
        ]
        for param_name, argument_setting in self.arguments.items():
            if param_name not in parsed_args:
                print(argument_setting)
                if argument_setting.default is not None:
                    parsed_args[param_name] = (
                        argument_setting.default,
                        argument_setting,
                    )
                else:
                    raise ExecutionStop()

        return (parsed_args, variables)

    def prefix_match(self, target_chain: MessageChain):
        target_chain = target_chain.as_merged()

        chain_frames: List[MessageChain] = target_chain.split(" ", raw_string=True)

        # 前缀匹配
        if len(self.prefixs) > len(chain_frames):
            return
        for index, current_prefix in enumerate(self.prefixs):
            current_frame = chain_frames[index]
            if not current_frame.__root__ or type(current_frame.__root__[0]) is not Text:
                return
            if current_frame.__root__[0].text != current_prefix:
                return

        chain_frames = chain_frames[len(self.prefixs) :]
        return MessageChain.create(
            list(itertools.chain(*[[*i.__root__, Text(" ")] for i in chain_frames]))[:-1]
        ).as_merged()

    async def beforeExecution(self, interface: DispatcherInterface):
        message_chain: MessageChain = await interface.lookup_param(
            "__literature_messagechain__", MessageChain, None, [[], 0]
        )
        if set([i.__class__ for i in message_chain.__root__]).intersection(BLOCKING_ELEMENTS):
            raise ExecutionStop()
        noprefix = self.prefix_match(message_chain)
        if noprefix is None:
            raise ExecutionStop()

        interface.broadcast.decorator_interface.local_storage[
            "literature_detect_result"
        ] = self.parse_message(noprefix)

    async def catch(self, interface: DispatcherInterface):
        if interface.name == "__literature_messagechain__":
            return

        result = interface.broadcast.decorator_interface.local_storage.get(
            "literature_detect_result"
        )
        if result:
            match_result, variargs = result
            if interface.default == "__literature_variables__":
                return variargs

            arg_fetch_result = match_result.get(interface.name)
            if arg_fetch_result:
                match_value, raw_argument = arg_fetch_result
                if isinstance(raw_argument, SwitchParameter):
                    return Force(match_value)
                elif interface.annotation is ParamPattern:
                    return raw_argument
                elif match_value is not None:
                    return match_value

    async def beforeTargetExec(self, interface: "DispatcherInterface", e, tb):
        if "literature_detect_result" in interface.broadcast.decorator_interface.local_storage:
            del interface.broadcast.decorator_interface.local_storage["literature_detect_result"]
