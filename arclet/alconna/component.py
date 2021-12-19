import re
from typing import Union, Dict, List, Any, Optional
from pydantic import BaseModel
from pydantic.utils import Representation

from . import split_once
from .exceptions import NullName, InvalidOptionName
from .types import NonTextElement, Args


class CommandInterface(BaseModel):
    name: str
    separator: str = " "

    def separate(self, sep: str):
        self.separator = sep
        return self

    class Config:
        arbitrary_types_allowed = True
        extra = "allow"


class OptionInterface(CommandInterface):
    type: str
    args: Args


class Option(OptionInterface):
    type: str = "OPT"

    def __init__(self, name: str, args: Optional[Args] = None, **kwargs):
        if name == "":
            raise NullName
        if re.match(r"^[`~?/.,<>;\':\"|!@#$%^&*()_+=\[\]}{]+.*$", name):
            raise InvalidOptionName
        super().__init__(
            name=name,
            args=args or Args(**kwargs)
        )

    def help(self, help_string: str):
        setattr(self, "help_doc", f"# {help_string}\n"
                                  f"  {self.name}{self.separator}{self.args.params(self.separator)}\n")
        return self


class Subcommand(OptionInterface):
    type: str = "SBC"
    options: List[Option]

    def __init__(self, name: str, *option: Option, args: Optional[Args] = None, **kwargs):
        if name == "":
            raise NullName
        if re.match(r"^[`~?/.,<>;\':\"|!@#$%^&*()_+=\[\]}{]+.*$", name):
            raise InvalidOptionName
        super().__init__(
            name=name,
            options=list(option),
            args=args or Args(**kwargs)
        )

    def help(self, help_string: str):
        option_string = "".join(list(map(lambda x: getattr(x, "help_doc", ""), self.options)))
        option_help = "## 该子命令内可用的选项有:\n " if option_string else ""
        setattr(self, "help_doc", f"# {help_string}\n"
                                  f"  {self.name}{self.separator}{self.args.params(self.separator)}\n"
                                  f"{option_help}{option_string}")
        return self


Options_T = List[OptionInterface]


class Arpamar(Representation):
    """
    亚帕玛尔(Arpamar), Alconna的珍藏宝书

    Example:
        1.`Arpamar.main_argument`: 当 Alconna 写入了 main_argument 时,该参数返回对应的解析出来的值

        2.`Arpamar.header`: 当 Alconna 的 command 内写有正则表达式时,该参数返回对应的匹配值

        3.`Arpamar.has`: 判断 Arpamar 内是否有对应的属性

        4.`Arpamar.get`: 返回 Arpamar 中指定的属性

        5.`Arpamar.matched`: 返回命令是否匹配成功

    """

    def __init__(self):
        self.current_index: int = 0  # 记录解析时当前字符串的index
        self.is_str: bool = False  # 是否解析的是string
        self.results: Dict[str, Any] = {'options': {}, 'main_args': {}}
        self.elements: Dict[int, NonTextElement] = {}
        self.raw_texts: List[List[Union[int, str]]] = []
        self.need_main_args: bool = False
        self.matched: bool = False
        self.head_matched: bool = False

        self._options: Dict[str, Any] = {}
        self._args: Dict[str, Any] = {}

    __slots__ = ["current_index", "is_str", "results", "elements", "raw_texts", "need_main_args", "matched",
                 "head_matched", "_options", "_args"]

    @property
    def main_args(self):
        if self.need_main_args:
            return self.results.get('main_args')

    @property
    def header(self):
        if 'header' in self.results:
            return self.results['header']
        else:
            return self.head_matched

    @property
    def all_matched_args(self):
        return {**self.results['main_args'], **self._args}

    @property
    def option_args(self):
        return self._args

    def encapsulate_result(self) -> None:
        if not self.results.get('header'):
            del self.results['header']
        for k, v in self.results['options'].items():
            self._options.setdefault(k, v)
            if isinstance(v, dict):
                for kk, vv in v.items():
                    if not isinstance(vv, dict):
                        self._args[kk] = vv
                    else:
                        self._args.update(vv)
        del self.results['options']

    def get(self, name: str) -> Union[Dict, str, NonTextElement]:
        if name in self._options:
            return self._options[name]
        elif name in self._args:
            return self._args[name]

    def has(self, name: str) -> bool:
        return any([name in self._args, name in self._options])

    def __getitem__(self, item: str):
        if item in self._options:
            return self._options[item]
        elif item in self._args:
            return self._args[item]

    def split_by(self, separate: str):
        _text: str = ""  # 重置
        _rest_text: str = ""

        if self.raw_texts[self.current_index][0]:  # 如果命令头匹配后还有字符串没匹配到
            _text, _rest_text = split_once(self.raw_texts[self.current_index][0], separate)

        elif not self.is_str and len(self.raw_texts) > 1:  # 如果命令头匹配后字符串为空则有两种可能，这里选择不止一段字符串
            self.current_index += 1
            _text, _rest_text = split_once(self.raw_texts[self.current_index][0], separate)

        return _text, _rest_text

    class Config:
        extra = 'allow'
