"""消息链处理器用到的工具函数, 类"""
import argparse
import inspect
import re
from contextvars import ContextVar
from typing import (
    TYPE_CHECKING,
    Callable,
    ClassVar,
    Dict,
    Final,
    List,
    Literal,
    NoReturn,
    Optional,
    Type,
    TypeVar,
    Union,
    overload,
)

from graia.amnesia.message.chain import MessageChain

from avilla.core.elements import Element, Notice, NoticeAll, Text
from avilla.core.utilles import identity

from .typing import T

if TYPE_CHECKING:
    from .twilight import Twilight

Element_T = TypeVar("Element_T", bound=Element)
elem_mapping_ctx: ContextVar[Dict[str, Element]] = ContextVar("elem_mapping_ctx")


def split(string: str, keep_quote: bool = False) -> List[str]:
    """尊重引号与转义的字符串切分

    Args:
        string (str): 要切割的字符串
        keep_quote (bool): 是否保留引号, 默认 False.

    Returns:
        List[str]: 切割后的字符串, 可能含有空格
    """
    result: List[str] = []
    quote = ""
    cache: List[str] = []
    for index, char in enumerate(string):
        if char in {"'", '"'}:
            if not quote:
                quote = char
            elif char == quote and index and string[index - 1] != "\\":  # is current quote, not transfigured
                quote = ""
            else:
                cache.append(char)
                continue
            if keep_quote:
                cache.append(char)
        elif not quote and char == " ":
            result.append("".join(cache))
            cache = []
        elif char != "\\":
            cache.append(char)
    if cache:
        result.append("".join(cache))
    return result


def gen_flags_repr(flags: re.RegexFlag) -> str:
    """通过 RegexFlag 生成对应的字符串

    Args:
        flags (re.RegexFlag): 正则表达式的标记

    Returns:
        str: 对应的标记字符串
    """
    flags_list: List[str] = []

    if re.ASCII in flags:
        flags_list.append("a")
    if re.IGNORECASE in flags:
        flags_list.append("i")
    if re.LOCALE in flags:
        flags_list.append("L")
    if re.MULTILINE in flags:
        flags_list.append("m")
    if re.DOTALL in flags:
        flags_list.append("s")
    if re.UNICODE in flags:
        flags_list.append("u")
    if re.VERBOSE in flags:
        flags_list.append("x")

    return "".join(flags_list)


def transform_regex(flag: re.RegexFlag, regex_pattern: str) -> str:
    """生成嵌套正则表达式字符串来达到至少最外层含有一个捕获组的效果

    Args:
        flag (re.RegexFlag): 正则表达式标记
        regex_pattern (str): 正则表达式字符串

    Returns:
        str: 转换后的正则表达式字符串
    """
    return f"(?{gen_flags_repr(flag)}:({regex_pattern}))" if flag else f"({regex_pattern})"


class MessageChainType:
    """用于标记类型为消息链, 在 ArgumentMatch 上使用"""

    @staticmethod
    def __call__(string: str) -> MessageChain:
        return _from_mapping_string(string, elem_mapping_ctx.get())


class ElementType:
    """用于标记类型为消息链元素, 在 ArgumentMatch 上使用"""

    def __init__(self, pattern: Type[Element_T]):
        self.regex = re.compile(f"\x02(\\d+)_{identity(pattern)}\x03")

    def __call__(self, string: str) -> Element:
        if not self.regex.fullmatch(string):
            raise ValueError(f"{string} not matching {self.regex.pattern}")
        return _from_mapping_string(string, elem_mapping_ctx.get())[0]


class UnmatchedClass:
    __slots__ = ()

    def __repr__(self) -> str:
        return "<Unmatched>"

    def __bool__(self) -> bool:
        return False


Unmatched = UnmatchedClass()


class TwilightParser(argparse.ArgumentParser):
    """适于 Twilight 使用的 argparse.ArgumentParser 子类
    移除了报错时自动退出解释器的行为
    """

    def error(self, message) -> NoReturn:
        raise ValueError(message)

    def accept_type(self, action: Union[str, type]) -> bool:
        """检查一个 action 是否接受 type 参数

        Args:
            action (Union[str, type]): 检查的 action

        Returns:
            bool: 是否接受 type 参数
        """
        if action is ...:
            action = "store"
        if isinstance(action, str):
            action_cls: Type[argparse.Action] = self._registry_get("action", action, action)
        elif isinstance(action, type) and issubclass(action, argparse.Action):
            action_cls = action
        else:
            return False
        action_init_sig = inspect.signature(action_cls.__init__)
        if "type" not in action_init_sig.parameters:
            return False
        return True


class TwilightHelpManager:
    AUTO_ID: Final[str] = "&auto_id" + hex(id("&auto_id"))
    _manager_ref: ClassVar[Dict[str, "TwilightHelpManager"]] = {}

    name: str
    display_name: Optional[str]
    help_map: Dict[str, "Twilight"]

    def __init__(self, name: str, display_name: Optional[str] = AUTO_ID):
        self.name: str = name
        self.help_map: Dict[str, Twilight] = {}
        if display_name == self.AUTO_ID:
            self.display_name = None if name.startswith(("global", "local", "_")) else name
        else:
            self.display_name = display_name
        if name in TwilightHelpManager._manager_ref:
            global_ref = TwilightHelpManager._manager_ref[name]
            global_ref.display_name = global_ref.display_name or display_name
            self.help_map = global_ref.help_map
        else:
            TwilightHelpManager._manager_ref[name] = self

    def register(self, twilight: "Twilight") -> None:
        if twilight.help_id == self.AUTO_ID:
            from .twilight import ElementMatch, ParamMatch, RegexMatch, UnionMatch

            extracted_ids: List[str] = []
            for match in twilight.matcher.origin_match_list:
                if isinstance(match, UnionMatch):
                    for i in match.pattern:
                        if isinstance(i, ElementMatch):
                            extracted_ids.append(i.type.__name__)
                        elif isinstance(i, RegexMatch):
                            if not isinstance(i, ParamMatch):
                                extracted_ids.append(i.pattern)
                        else:
                            extracted_ids.append(i)
                elif isinstance(match, ElementMatch):
                    extracted_ids.append(match.type.__name__)
                elif isinstance(match, RegexMatch) and not isinstance(match, ParamMatch):
                    extracted_ids.append(match.pattern)
            if not extracted_ids:
                raise ValueError(f"Unable to extract help_id from {twilight}")
            help_id = extracted_ids[0]
        else:
            help_id = twilight.help_id
        if help_id in self.help_map and self.help_map[help_id] is not twilight:
            raise ValueError(
                f"Help Manager {self.name}'s help id {help_id} has been registered", self.help_map[help_id]
            )
        self.help_map[help_id] = twilight

    @classmethod
    def get_help_mgr(cls, mgr: Union["TwilightHelpManager", str]) -> "TwilightHelpManager":
        return TwilightHelpManager(mgr) if isinstance(mgr, str) else mgr

    @overload
    def get_help(
        self,
        description: str = "",
        epilog: str = "",
        *,
        prefix_src: Literal["brief", "usage", "description"] = "brief",
        fmt_cls: Type[argparse.HelpFormatter] = argparse.HelpFormatter,
    ) -> str:
        ...

    @overload
    def get_help(
        self,
        description: str = "",
        epilog: str = "",
        *,
        prefix_src: Literal["brief", "usage", "description"] = "brief",
        fmt_func: Callable[[str], T],
        fmt_cls: Type[argparse.HelpFormatter] = argparse.HelpFormatter,
    ) -> T:
        ...

    def get_help(
        self,
        description: str = "",
        epilog: str = "",
        *,
        prefix_src: Literal["brief", "usage", "description"] = "brief",
        fmt_func: Optional[Callable[[str], T]] = None,
        fmt_cls: Type[argparse.HelpFormatter] = argparse.HelpFormatter,
    ) -> Union[T, str]:
        """获取本管理器总的帮助信息

        Args:
            fmt_func (Optional[Callable[[str], T]]): 如果指定, 则使用该函数来转换帮助信息格式
            fmt_cls (Type[argparse.HelpFormatter], optional): 如果指定, 则使用该类来格式化帮助信息. \
                默认为 argparse.HelpFormatter
        """
        formatter = fmt_cls("")
        formatter.add_usage(self.display_name or "", [], [], "")

        formatter.add_text(description)

        if self.help_map:
            formatter.start_section(f"共有 {len(self.help_map)} 个子匹配")
            for help_id, twilight in self.help_map.items():
                if twilight.help_data is not None:
                    prefixes: Dict[str, str] = {
                        "brief": twilight.help_brief,
                        "usage": twilight.help_data["usage"],
                        "description": twilight.help_data["description"],
                    }
                    formatter.add_text(f"{help_id} - {prefixes[prefix_src]}")
                else:
                    formatter.add_text(f"{help_id}")
            formatter.end_section()

        formatter.add_text(epilog)

        help_string: str = formatter.format_help()
        return fmt_func(help_string) if fmt_func else help_string


def _to_mapping_str(
    chain: MessageChain,
    *,
    remove_source: bool = True,
    remove_quote: bool = True,
    remove_extra_space: bool = False,
) -> tuple[str, Dict[str, Element]]:
    """转换消息链为映射字符串与映射字典的元组.
    Args:
        remove_source (bool, optional): 是否移除消息链中的 Source 元素. 默认为 True.
        remove_quote (bool, optional): 是否移除消息链中的 Quote 元素. 默认为 True.
        remove_extra_space (bool, optional): 是否移除 Quote At AtAll 的多余空格. 默认为 False.
    Returns:
        Tuple[str, Dict[str, Element]]: 生成的映射字符串与映射字典的元组
    """
    elem_mapping: Dict[str, Element] = {}
    elem_str_list: List[str] = []
    for i, elem in enumerate(chain.content):
        if not isinstance(elem, Text):
            elem_mapping[str(i)] = elem
            elem_str_list.append(f"\x02{i}_{identity(elem)}\x03")
        elif (
            remove_extra_space
            and i  # not first element
            and isinstance(
                chain.content[i - 1], (Notice, NoticeAll)
            )  # following elements which have an dumb trailing space
            and elem.text.startswith("  ")  # extra space (count >= 2)
        ):
            elem_str_list.append(elem.text[1:])
        else:
            elem_str_list.append(elem.text)
    return "".join(elem_str_list), elem_mapping


__element_pattern = re.compile("(\x02\\w+\x03)")


def gen_subclass(cls: type[T]):  # pyright: ignore
    """生成某个类的所有子类 (包括其自身)

    Args:
        cls (Type[T]): 类

    Yields:
        Type[T]: 子类
    """
    yield cls
    for sub_cls in cls.__subclasses__():
        if TYPE_CHECKING:
            assert issubclass(sub_cls, cls)
        yield from gen_subclass(sub_cls)


ELEMENT_MAPPING: Dict[str, Type[Element]] = {identity(i): i for i in gen_subclass(Element)}


def _from_mapping_string(string: str, mapping: Dict[str, Element]) -> MessageChain:
    """从映射字符串与映射字典的元组还原消息链.
    Args:
        string (str): 映射字符串
        mapping (Dict[int, Element]): 映射字典.
    Returns:
        MessageChain: 构建的消息链
    """
    elements: List[Element] = []
    for x in __element_pattern.split(string):
        if x:
            if x[0] == "\x02" and x[-1] == "\x03":
                index, class_name = x[1:-1].split("_")
                if not isinstance(mapping[index], ELEMENT_MAPPING[class_name]):
                    raise ValueError("Validation failed: not matching element type!")
                elements.append(mapping[index])
            else:
                elements.append(Text(x))
    return MessageChain(elements)
