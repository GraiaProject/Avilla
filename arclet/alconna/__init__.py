from typing import Dict, List, Optional, Union, Any, overload
import re

from avilla.core.message import Element
from .util import split_once, split
from .component import Option, Subcommand, AlconnaMatch
from .types import Args
# from .exceptions import ParamsUnmatched, NullName, InvalidFormatMap, NullTextMessage


class Alconna:
    """
    亚尔康娜（Alconna），Cesloi 的妹妹

    用于更加精确的命令解析，支持String与MessageChain

    样例: Alconna(
        headers=[""],
        command="name",
        options=[
            Subcommand("sub_name",Option("sub-opt", sub_arg=sub_arg), args=sub_main_arg),
            Option("opt", arg=arg)
        ]
        main_args=main_args
    )

    其中
        - name: 命令名称
        - sub_name: 子命令名称
        - sub-opt: 子命令选项名称
        - sub_arg: 子命令选项参数
        - sub_main_arg: 子命令主参数
        - opt: 命令选项名称
        - arg: 命令选项参数

    Args:
        headers: 呼叫该命令的命令头，一般是你的机器人的名字或者符号，与 command 至少有一个填写
        command: 命令名称，你的命令的名字，与 headers 至少有一个填写
        options: 命令选项，你的命令可选择的所有 option ，包括子命令与单独的选项
        main_args: 主参数，填入后当且仅当命令中含有该参数时才会成功解析
    """

    headers: List[str]
    command: str
    options: List[Option]
    main_args: Args

    def __init__(
            self,
            headers: List[str] = None,
            command: Optional[str] = None,
            options: List[Option] = None,
            main_args: Optional[Args] = None,
            exception_in_time: bool = False,
            **kwargs

    ):
        # headers 与 command 二者必须有其一
        if all([all([not headers, not command]), not options, not main_args]):
            raise TypeError("headers and command can not be None at the same time")
        self.headers = headers or [""]
        self.command = command or ""
        self.options = options or []
        self.main_args = main_args or Args(**kwargs)
        self.exception_in_time = exception_in_time
        self._initialise_arguments()

    @classmethod
    @overload
    def format(
            cls,
            format_string: str,
            format_args: List[Union[str, Element, Args, Option, List[Option]]],
            reflect_map: Dict[str, str] = None
    ) -> "Alconna":
        ...

    @classmethod
    @overload
    def format(
            cls,
            format_string: str,
            format_args: Dict[str, Union[str, Element, Args, Option, List[Option]]],
            reflect_map: Dict[str, str] = None
    ) -> "Alconna":
        ...

    @classmethod
    def format(
            cls,
            format_string: str,
            format_args: ...,
            reflect_map: Optional[Dict[str, str]] = None
    ) -> "Alconna":
        strings: List[str] = split(format_string)
        command = strings.pop(0)
        options = []
        main_args = None

        _string_stack: List[str] = list()
        for index, str_value in enumerate(strings):
            arg = re.findall(r"{(.+)}", str_value)
            if not arg:
                _string_stack.append(str_value)
                continue

            key = arg[0] if not reflect_map else (reflect_map[arg[0]] if reflect_map.get(arg[0]) else arg[0])

            if isinstance(format_args, List) and arg[0].isdigit():
                value = format_args[int(arg[0])]
            elif isinstance(format_args, Dict):
                value = format_args[arg[0]]
            else:
                raise TypeError(f"format_args must be List or Dict, but {type(format_args)}")

            stack_count = len(_string_stack)
            if stack_count == 2:
                sub_name, opt_name = _string_stack
                if isinstance(value, Args):
                    options.append(Subcommand(sub_name, Option(opt_name, args=value)))
                elif not isinstance(value, Option) and not isinstance(value, List):
                    options.append(Subcommand(sub_name, Option(opt_name, **{key: value})))
                _string_stack.clear()

            if stack_count == 1:
                may_name = _string_stack.pop(0)
                if isinstance(value, Option):
                    options.append(Subcommand(may_name, value))
                elif isinstance(value, List):
                    options.append(Subcommand(may_name, *value))
                elif isinstance(value, Args):
                    options.append(Option(may_name, args=value))
                else:
                    options.append(Option(may_name, **{key: value}))

            if stack_count == 0:
                if index == 0:
                    if isinstance(value, Args):
                        main_args = value
                    elif not isinstance(value, Option) and not isinstance(value, List):
                        main_args = Args(**{key: value})
                    else:
                        if isinstance(value, Option):
                            options.append(value)
                        elif isinstance(value, list):
                            options[-1].options.extend(value)
                        elif isinstance(value, Args):
                            options[-1].args = value
                        else:
                            options[-1].args.args.update({key: value})

        alc = cls(command=command, options=options, main_args=main_args)
        return alc

    def add_options(self, options: List[Union[Option, Subcommand]]):
        self.options.extend(options)
        self._initialise_arguments()

    def _initialise_arguments(self):
        # todo: GreyElaina. WTF.
        # params是除开命令头的剩下部分
        self._params: Dict[str, Union[Args, Dict[str, Any]]] = {"main_args": self.main_args}
        for opts in self.options:
            if isinstance(opts, Subcommand):
                if opts.sub_params is None:
                    opts.sub_params = {}
                opts.setdefault('sub_params', {"sub_args": opts['args']})
                for sub_opts in opts['options']:
                    opts['sub_params'][sub_opts['name']] = sub_opts
            self._params[opts['name']] = opts

        self._command_headers: List[str] = []  # 依据headers与command生成一个列表，其中含有所有的命令头
        if self.headers != [""]:
            for i in self.headers:
                self._command_headers.append(i + self.command)
        elif self.command:
            self._command_headers.append(self.command)

    def _analyse_args(
            self,
            opt_args: Args,
            may_args: str,
            sep: str,
            rest_text: str
    ) -> Dict[str, Any]:

        _option_dict: Dict[str, Any] = {}
        for k, v in opt_args:
            if isinstance(v, str):
                if sep != self.separator:
                    may_arg, may_args = split_once(may_args, sep)
                else:
                    may_arg, rest_text = self.result.split_by(sep)
                if not (_arg_find := re.findall('^' + v + '$', may_arg)):
                    if (default := opt_args.check(k)) is not None:
                        _arg_find = [default]
                    else:
                        raise ParamsUnmatched(f"this param {may_arg} does not right")
                if may_arg == v:
                    _arg_find[0] = Ellipsis
                _option_dict[k] = _arg_find[0]
                if sep == self.separator:
                    self.result.raw_texts[self.result.current_index][0] = rest_text
            else:
                may_element_index = self.result.raw_texts[self.result.current_index][1] + 1
                if type(self.result.elements[may_element_index]) is v:
                    _option_dict[k] = self.result.elements.pop(may_element_index)
                elif (default := opt_args.check(k)) is not None:
                    _option_dict[k] = default
                else:
                    raise ParamsUnmatched(
                        f"this element type {type(self.result.elements[may_element_index])} does not right")
        return _option_dict

    def _analyse_option(
            self,
            param: Dict[str, Union[str, Args]],
            text: str,
            rest_text: str
    ) -> Dict[str, Any]:

        opt: str = param['name']
        args: Args = param['args']
        sep: str = param['separator']
        name, may_args = split_once(text, sep)
        if sep == self.separator:  # 在sep等于separator的情况下name是被提前切出来的
            name = text
        if not re.match('^' + opt + '$', name):  # 先匹配选项名称
            raise ParamsUnmatched(f"{name} dose not matched with {opt}")
        self.result.raw_texts[self.result.current_index][0] = rest_text
        name = name.lstrip("-")
        if args.empty:
            return {name: Ellipsis}
        return {name: self._analyse_args(args, may_args, sep, rest_text)}

    def _analyse_subcommand(
            self,
            param: Dict[str, Union[str, Dict, Args]],
            text: str,
            rest_text: str
    ) -> Dict[str, Any]:
        command: str = param['name']
        sep: str = param['separator']
        sub_params: Dict = param['sub_params']
        name, may_text = split_once(text, sep)
        if sep == self.separator:
            name = text
        if not re.match('^' + command + '$', name):
            raise ParamsUnmatched(f"{name} dose not matched with {command}")

        self.result.raw_texts[self.result.current_index][0] = may_text
        if sep == self.separator:
            self.result.raw_texts[self.result.current_index][0] = rest_text

        name = name.lstrip("-")
        if param['args'].empty and not param['options']:
            return {name: Ellipsis}

        subcommand = {}
        _get_args = False
        for i in range(len(sub_params)):
            try:
                _text, _rest_text = self.result.split_by(sep)
                if not (sub_param := sub_params.get(_text)):
                    sub_param = sub_params['sub_args']
                    for sp in sub_params:
                        if _text.startswith(sp):
                            sub_param = sub_params.get(sp)
                            break
                if isinstance(sub_param, dict):
                    # if sub_param.get('type'):
                    subcommand.update(self._analyse_option(sub_param, _text, _rest_text))
                elif not _get_args:
                    if args := self._analyse_args(sub_param, _text, sep, _rest_text):
                        _get_args = True
                        subcommand.update(args)
            except (IndexError, KeyError):
                continue
            except ParamsUnmatched:
                if self.exception_in_time:
                    raise
                break

        if sep != self.separator:
            self.result.raw_texts[self.result.current_index][0] = rest_text
        return {name: subcommand}

    def _analyse_header(self) -> str:
        head_text, self.result.raw_texts[0][0] = self.result.split_by(self.separator)
        for ch in self._command_headers:
            if not (_head_find := re.findall('^' + ch + '$', head_text)):
                continue
            self.result.head_matched = True
            if _head_find[0] != ch:
                return _head_find[0]
        if not self.result.head_matched:
            raise ParamsUnmatched(f"{head_text} does not matched")

    def analyse_message(self, message: Union[str, MessageChain]) -> Arpamar:
        if hasattr(self, "result"):
            del self.result
        self.result: Arpamar = Arpamar()

        if not self.main_args.empty:
            self.result.need_main_args = True  # 如果need_marg那么match的元素里一定得有main_argument

        if isinstance(message, str):
            self.result.is_str = True
            self.result.raw_texts.append([message, 0])
        else:
            for i, ele in enumerate(message):
                if ele.__class__.__name__ not in ("Plain", "Source", "Quote", "File"):
                    self.result.elements[i] = ele
                elif ele.__class__.__name__ == "Plain":
                    self.result.raw_texts.append([ele.text.lstrip(' '), i])

        if not self.result.raw_texts:
            if self.exception_in_time:
                raise NullTextMessage
            self.result.results.clear()
            return self.result

        try:
            self.result.results['header'] = self._analyse_header()
        except ParamsUnmatched:
            self.result.results.clear()
            return self.result

        for i in range(len(self._params)):
            if all([t[0] == "" for t in self.result.raw_texts]):
                break
            try:
                _text, _rest_text = self.result.split_by(self.separator)
                _param = self._params.get(_text)
                if not _param:
                    _param = self._params['main_args']
                    for p in self._params:
                        if _text.startswith(p):
                            _param = self._params.get(p)
                            break
                if isinstance(_param, dict):
                    if _param['type'] == 'OPT':
                        self.result.results['options'].update(self._analyse_option(_param, _text, _rest_text))
                    elif _param['type'] == 'SBC':
                        self.result.results['options'].update(self._analyse_subcommand(_param, _text, _rest_text))
                elif not self.result.results.get("main_args"):
                    self.result.results['main_args'] = self._analyse_args(_param, _text, self.separator, _rest_text)
            except (IndexError, KeyError):
                pass
            except ParamsUnmatched:
                if self.exception_in_time:
                    raise
                break

        try:
            may_element_index = self.result.raw_texts[self.result.current_index][1] + 1
            for k, v in self.main_args:
                if type(self.result.elements[may_element_index]) is v:
                    self.result.results['main_args'][k] = self.result.elements.pop(may_element_index)
                elif (default := self.main_args.check(k)) is not None:
                    self.result.results['main_args'][k] = default
                else:
                    raise ParamsUnmatched(
                        f"this element type {type(self.result.elements[may_element_index])} does not right")
        except (KeyError, IndexError):
            pass
        except ParamsUnmatched:
            if self.exception_in_time:
                raise
            pass

        if len(self.result.elements) == 0 and all([t[0] == "" for t in self.result.raw_texts]) \
                and (not self.result.need_main_args or (
                self.result.need_main_args and not self.result.has('help') and self.result.results.get('main_args')
                )
        ):
            self.result.matched = True
            self.result.encapsulate_result()
        else:
            if self.exception_in_time:
                raise ParamsUnmatched(", ".join([t[0] for t in self.result.raw_texts]))
            self.result.results.clear()
        return self.result
