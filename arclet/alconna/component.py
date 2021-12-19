import re
from typing import Union, Dict, List, Any, Optional, cast
from dataclasses import dataclass

from . import split_once
from .types import Args
from avilla.core.message import Element  # 原文里是 NonTextElement, 这里懒得写了.


@dataclass
class Option:
    name: str
    args: Args
    separator: str = " "

    def __init__(self, name: str, args: Optional[Args] = None, **kwargs):
        if name == "":
            raise ValueError("name cannot be empty")
        if re.match(r"^[`~?/.,<>;\':\"|!@#$%^&*()_+=\[\]}{]+.*$", name):
            raise TypeError("name cannot contain special characters")
        self.name = name
        self.args = args or Args(**kwargs)

    def separate(self, sep: str):
        self.separator = sep
        return self


@dataclass
class Subcommand(Option):
    args: Args
    options: List[Option]
    sub_params: Dict[str, Option] = None

    @property
    def separator(self):
        raise NotImplementedError("Subcommand does not support separator.")

    def separate(self, sep: str):
        raise NotImplementedError("Subcommand does not support separator.")

    def __init__(self, name: str, *option: Option, args: Optional[Args] = None, **kwargs):
        if not name:
            raise ValueError("Subcommand name cannot be empty.")
        if re.match(r"^[`~?/.,<>;\':\"|!@#$%^&*()_+=\[\]}{]+.*$", name):
            raise TypeError("Subcommand name cannot contain special characters.")
        self.name = name
        self.args = args or Args(**kwargs)
        self.options = list(option)


class AlconnaMatch:
    """
    AlconnaMatch, 原名是亚帕玛尔(Arpamar), 设定上是 Alconna 的珍藏宝书, 这里 Avilla 改成了易于维护的名称.

    Example:
        1.`AlconnaMatch.main_argument`: 当 Alconna 写入了 main_argument 时,该参数返回对应的解析出来的值

        2.`AlconnaMatch.header`: 当 Alconna 的 command 内写有正则表达式时,该参数返回对应的匹配值

        3.`AlconnaMatch.has`: 判断 AlconnaMatch 内是否有对应的属性

        4.`AlconnaMatch.get`: 返回 AlconnaMatch 中指定的属性

        5.`AlconnaMatch.matched`: 返回命令是否匹配成功

    """

    __slots__ = ("current_index", "is_str", "results", "elements", "raw_texts", "need_main_args", "matched",
                 "head_matched", "_options", "_args")

    def __init__(self):
        self.current_index: int = 0  # 记录解析时当前字符串的index
        self.is_str: bool = False  # 是否解析的是string
        self.results: Dict[str, Any] = {'options': {}, 'main_args': {}}
        self.elements: Dict[int, Element] = {}
        self.raw_texts: List[List[Union[int, str]]] = []
        self.need_main_args: bool = False
        self.matched: bool = False
        self.head_matched: bool = False

        self._options: Dict[str, Any] = {}
        self._args: Dict[str, Any] = {}

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

    def get(self, name: str) -> Union[Dict, str, Element, None]:
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
            _text, _rest_text = split_once(cast(str, self.raw_texts[self.current_index][0]), separate)

        elif not self.is_str and len(self.raw_texts) > 1:  # 如果命令头匹配后字符串为空则有两种可能，这里选择不止一段字符串
            self.current_index += 1
            _text, _rest_text = split_once(cast(str, self.raw_texts[self.current_index][0]), separate)

        return _text, _rest_text
