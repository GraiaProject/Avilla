from __future__ import annotations

from collections.abc import Iterable, Iterator
from copy import deepcopy
from typing import TYPE_CHECKING, Any, ClassVar, Sequence, TypeVar, overload

from typing_extensions import Self

from .element import Element, Text

if TYPE_CHECKING:
    E = TypeVar("E", bound=Element)


class MessageChain:
    """即 "消息链", 被用于承载整个消息内容的数据结构, 包含有一有序列表, 包含有继承了 Element 的各式类实例.

    - 你可以通过实例化 `MessageChain` 创建一个消息链

    - `str(chain)`: 获取字符串形式表示的消息

    - `has`: 判断特定的内容是否存在于消息链中

    - `get`: 获取消息链中的所有特定类型的元素

    - `get_first`: 获取消息链中的第 1 个特定类型的元素

    - `get_one`: 获取消息链中的第 index + 1 个特定类型的元素

    - `merge`: 将消息链中相邻的 Text 元素合并为一个 Text 元素.

    - `startswith`: 判断消息链是否以指定的文本开头

    - `endswith`: 判断消息链是否以指定的文本结尾

    - `include`: 创建只包含指定元素类型的消息链

    - `exclude`: 创建排除指定元素类型的消息链

    - `split`: 用指定文本将消息链拆分为多个

    - `append`: 将指定的元素添加到消息链的末尾

    - `extend`: 将指定的序列/消息链添加到消息链的末尾

    - `only`: 检查是否只包含指定元素

    - `index`: 获取指定元素在消息链中的索引

    - `index_sub`: 搜索子消息链在本消息链的出现位置

    - `count`: 获取消息链中指定元素的数量

    - `copy`: 获取消息链的拷贝

    - `chain.join(chains)`: 拼接多个消息链并插入指定内容

    - `removeprefix`: 尝试移除前缀

    - `removesuffix`: 尝试移除后缀

    - `replace`: 替换消息链的一部分

    """

    content: list[Element]

    def __init__(self, elements: list[Element]):
        """从传入的序列(可以是元组 tuple, 也可以是列表 list) 创建消息链.
        Args:
            elements (list[T]): 包含且仅包含消息元素的序列
        Returns:
            MessageChain: 以传入的序列作为所承载消息的消息链
        """
        self.content = elements

    def has(self, item: Element | type[Element] | Self | Sequence[str | Element]) -> bool:
        """
        判断消息链中是否含有特定的内容.

        Args:
            item (Element | type[Element] | Self | Sequence[str | Element]): 需要判断的元素/元素类型/消息链/字符串/元素列表.

        Returns:
            bool: 判断结果
        """
        if isinstance(item, type):
            return item in [type(i) for i in self.content]
        if isinstance(item, Element):
            return item in self.merge().content
        if isinstance(item, (Sequence, MessageChain)):
            return bool(self.index_sub(item))

        raise ValueError(f"{item} is not an acceptable argument!")

    def get(self, element_class: type[E], count: int = -1) -> list[E]:
        """
        获取消息链中所有特定类型的消息元素

        Args:
            element_class (type[E]): 指定的消息元素的类型, 例如 "Plain", "At", "Image" 等.
            count (int, optional): 至多获取的元素个数

        Returns:
            list[E]: 获取到的符合要求的所有消息元素; 另: 可能是空列表([]).
        """
        if count == -1:
            count = len(self.content)
        return [i for i in self.content if isinstance(i, element_class)][:count]

    def get_one(self, element_class: type[E], index: int) -> E:
        """获取消息链中第 index + 1 个特定类型的消息元素
        Args:
            element_class (type[Element]): 指定的消息元素的类型, 例如 "Text", "Notice", "Image" 等.
            index (int): 索引, 从 0 开始数
        Returns:
            T: 消息链第 index + 1 个特定类型的消息元素
        """
        return self.get(element_class)[index]

    def get_first(self, element_class: type[E]) -> E:
        """获取消息链中第 1 个特定类型的消息元素
        Args:
            element_class (type[Element]): 指定的消息元素的类型, 例如 "Text", "Notice", "Image" 等.
        Returns:
            T: 消息链第 1 个特定类型的消息元素
        """
        return self.get(element_class)[0]

    def __str__(self) -> str:
        """获取以字符串形式表示的消息链, 且趋于通常你见到的样子.
        Returns:
            str: 以字符串形式表示的消息链
        """
        return "".join(str(i) for i in self.content)

    def join(self, *chains: Self | Iterable[Self]) -> Self:
        """将多个消息链连接起来, 并在其中插入自身.

        Args:
            *chains (Iterable[MessageChain]): 要连接的消息链.

        Returns:
            MessageChain: 连接后的消息链, 已对文本进行合并.
        """
        result: list[Element] = []
        list_chains: list[MessageChain] = []
        for chain in chains:
            if isinstance(chain, MessageChain):
                list_chains.append(chain)
            else:
                list_chains.extend(chain)

        for chain in list_chains:
            if chain is not list_chains[0]:
                result.extend(deepcopy(self.content))
            result.extend(deepcopy(chain.content))
        return self.__class__(result).merge()

    __contains__ = has

    @overload
    def __getitem__(self, item: type[E]) -> list[E]:
        ...

    @overload
    def __getitem__(self, item: int) -> Element:
        ...

    @overload
    def __getitem__(self, item: slice) -> Self:
        ...

    def __getitem__(self, item: type[Element] | int | slice) -> Any:
        """取出子消息链, 或元素.

        通过 `type` 取出属于 `type` 的元素列表

        通过 `int` 取出对应位置元素.

        通过 `slice` 取出子消息链.

        Args:
            item (type[Element] | int | slice): 索引项

        Returns:
            list[Element] | Element | MessageChain: 索引结果.
        """
        if isinstance(item, slice):
            return self.__class__(self.content[item])
        if isinstance(item, int):
            return self.content[item]
        elif issubclass(item, Element):
            return self.get(item)
        else:
            raise NotImplementedError("{0} is not allowed for item getting".format(type(item)))

    def merge(self) -> Self:
        """合并相邻的 Text 项, 并返回一个新的消息链实例

        Returns:
            MessageChain: 得到的新的消息链实例, 里面不应存在有任何的相邻的 Text 元素.
        """

        result = []

        texts = []
        for i in self.content:
            if not isinstance(i, Text):
                if texts:
                    result.append(__text_element_class__("".join(texts)))
                    texts.clear()  # 清空缓存
                result.append(i)
            else:
                texts.append(i.text)
        if texts:
            result.append(__text_element_class__("".join(texts)))
            texts.clear()  # 清空缓存
        return self.__class__(result)

    def exclude(self, *types: type[Element]) -> Self:
        """将除了在给出的消息元素类型中符合的消息元素重新包装为一个新的消息链
        Args:
            *types (type[Element]): 将排除在外的消息元素类型
        Returns:
            MessageChain: 返回的消息链中不包含参数中给出的消息元素类型
        """
        return self.__class__([i for i in self.content if not isinstance(i, types)])

    def include(self, *types: type[Element]) -> Self:
        """将只在给出的消息元素类型中符合的消息元素重新包装为一个新的消息链
        Args:
            *types (type[Element]): 将只包含在内的消息元素类型
        Returns:
            MessageChain: 返回的消息链中只包含参数中给出的消息元素类型
        """
        return self.__class__([i for i in self.content if isinstance(i, types)])

    def split(self, pattern: str = " ", raw_string: bool = False) -> list[Self]:
        """和 `str.split` 差不多, 提供一个字符串, 然后返回分割结果.

        Args:
            pattern (str): 分隔符. 默认为单个空格.
            raw_string (bool): 是否要包含 "空" 的文本元素.

        Returns:
            list[Self]: 分割结果, 行为和 `str.split` 差不多.
        """

        result: list[Self] = []
        tmp = []
        for element in self.content:
            if isinstance(element, Text):
                split_result = element.text.split(pattern)
                for index, split_str in enumerate(split_result):
                    if tmp and index > 0:
                        result.append(self.__class__(tmp))
                        tmp = []
                    if split_str or raw_string:
                        tmp.append(__text_element_class__(split_str))
            else:
                tmp.append(element)
        if tmp:
            result.append(self.__class__(tmp))
            tmp = []
        return result

    def __repr__(self) -> str:
        return f"MessageChain({repr(self.content)})"

    def __iter__(self) -> Iterator[Element]:
        yield from self.content

    def __len__(self) -> int:
        return len(self.content)

    def startswith(self, string: str) -> bool:
        """判断消息链是否以给出的字符串开头

        Args:
            string (str): 字符串

        Returns:
            bool: 是否以给出的字符串开头
        """

        if not self.content or not isinstance(self.content[0], Text):
            return False
        return self.content[0].text.startswith(string)

    def endswith(self, string: str) -> bool:
        """判断消息链是否以给出的字符串结尾

        Args:
            string (str): 字符串

        Returns:
            bool: 是否以给出的字符串结尾
        """

        if not self.content or not isinstance(self.content[-1], Text):
            return False
        return self.content[-1].text.endswith(string)

    def only(self, *element_classes: type[Element]) -> bool:
        """判断消息链中是否只含有特定类型元素.

        Args:
            *element_classes (type[Element]): 元素类型

        Returns:
            bool: 判断结果
        """
        return all(isinstance(i, element_classes) for i in self.content)

    def append(self, element: Element | str, copy: bool = False) -> Self:
        """
        向消息链最后追加单个元素

        Args:
            element (Element): 要添加的元素
            copy (bool): 是否要在副本上修改.

        Returns:
            MessageChain: copy = True 时返回副本, 否则返回自己的引用.
        """
        chain_ref = self.copy() if copy else self
        if isinstance(element, str):
            element = __text_element_class__(element)
        chain_ref.content.append(element)
        return chain_ref

    def extend(
        self,
        *content: Self | Element | list[Element | str],
        copy: bool = False,
    ) -> Self:
        """
        向消息链最后添加元素/元素列表/消息链

        Args:
            *content (MessageChain | Element | list[Element | str]): 要添加的元素/元素容器.
            copy (bool): 是否要在副本上修改.

        Returns:
            MessageChain: copy = True 时返回副本, 否则返回自己的引用.
        """
        result = []
        for i in content:
            if isinstance(i, Element):
                result.append(i)
            elif isinstance(i, str):
                result.append(__text_element_class__(i))
            elif isinstance(i, MessageChain):
                result.extend(i.content)
            else:
                for e in i:
                    if isinstance(e, str):
                        result.append(__text_element_class__(e))
                    else:
                        result.append(e)
        if copy:
            return self.__class__(deepcopy(self.content) + result)
        self.content.extend(result)
        return self

    def copy(self) -> Self:
        """
        拷贝本消息链.

        Returns:
            MessageChain: 拷贝的副本.
        """
        return self.__class__(deepcopy(self.content))

    def index(self, element_type: type[Element]) -> int | None:
        """
        寻找第一个特定类型的元素, 并返回其下标.

        Args:
            element_type (type[Element]): 元素或元素类型

        Returns:
            int | None: 元素下标, 若未找到则为 None.

        """
        return next((i for i, e in enumerate(self.content) if isinstance(e, element_type)), None)

    def count(self, element: type[Element] | Element) -> int:
        """
        统计共有多少个指定的元素.

        Args:
            element (type[Element] | Element): 元素或元素类型

        Returns:
            int: 元素数量
        """
        if isinstance(element, Element):
            return sum(i == element for i in self.content)
        return sum(isinstance(i, element) for i in self.content)

    def index_sub(self, sub: MessageChain | Sequence[str | Element]) -> list[int]:
        """判断消息链是否含有子链. 使用 KMP 算法.

        Args:
            sub (MessageChain | Sequence[str | Element]): 要判断的子链.

        Returns:
            List[int]: 所有找到的下标.
        """

        def unzip(seq: Sequence[str | Element]) -> list[str | Element]:
            res: list[str | Element] = []
            for e in seq:
                if isinstance(e, Text):
                    res.extend(e.text)
                elif isinstance(e, str):
                    res.extend(e)
                else:
                    res.append(e)
            return res

        pattern: list[str | Element] = unzip(sub.content) if isinstance(sub, MessageChain) else unzip(sub)

        match_target: list[str | Element] = unzip(self.content)

        if len(match_target) < len(pattern):
            return []

        fallback: list[int] = [0 for _ in pattern]
        current_fb: int = 0  # current fallback index
        for i in range(1, len(pattern)):
            while current_fb and pattern[i] != pattern[current_fb]:
                current_fb = fallback[current_fb - 1]
            if pattern[i] == pattern[current_fb]:
                current_fb += 1
            fallback[i] = current_fb

        match_index: list[int] = []
        ptr = 0
        for i, e in enumerate(match_target):
            while ptr and e != pattern[ptr]:
                ptr = fallback[ptr - 1]
            if e == pattern[ptr]:
                ptr += 1
            if ptr == len(pattern):
                match_index.append(i - ptr + 1)
                ptr = fallback[ptr - 1]
        return match_index

    def removeprefix(self, prefix: str, *, copy: bool = True) -> Self:
        """移除消息链前缀.

        Args:
            prefix (str): 要移除的前缀.
            copy (bool, optional): 是否在副本上修改, 默认为 True.

        Returns:
            MessageChain: 修改后的消息链, 若未移除则原样返回.
        """
        elements = deepcopy(self.content) if copy else self.content
        if not elements or not isinstance(elements[0], Text):
            return self.copy() if copy else self
        if elements[0].text.startswith(prefix):
            elements[0].text = elements[0].text[len(prefix) :]
        if copy:
            return self.__class__(elements)
        self.content.clear()
        self.content.extend(elements)
        return self

    def removesuffix(self, suffix: str, *, copy: bool = True) -> Self:
        """移除消息链后缀.

        Args:
            suffix (str): 要移除的后缀.
            copy (bool, optional): 是否在副本上修改, 默认为 True.

        Returns:
            MessageChain: 修改后的消息链, 若未移除则原样返回.
        """
        elements = deepcopy(self.content) if copy else self.content
        if not elements or not isinstance(elements[-1], Text):
            return self.copy() if copy else self
        last_elem: Text = elements[-1]
        if last_elem.text.endswith(suffix):
            last_elem.text = last_elem.text[: -len(suffix)]
        if copy:
            return self.__class__(elements)
        self.content.clear()
        self.content.extend(elements)
        return self

    def replace(
        self,
        old: MessageChain | list[Element],
        new: MessageChain | list[Element],
    ) -> Self:
        """替换消息链中的一部分. (在副本上操作)

        Args:
            old (MessageChain): 要替换的消息链.
            new (MessageChain): 替换后的消息链.

        Returns:
            MessageChain: 修改后的消息链, 若未替换则原样返回.
        """
        if not isinstance(old, MessageChain):
            old = MessageChain(old)
        if not isinstance(new, MessageChain):
            new = MessageChain(new)
        index_list: list[int] = self.index_sub(old)

        def unzip(chain: Self) -> list[str | Element]:
            unzipped: list[str | Element] = []
            for e in chain.content:
                if isinstance(e, Text):
                    unzipped.extend(e.text)
                else:
                    unzipped.append(e)
            return unzipped

        unzipped_new: list[str | Element] = unzip(new)
        unzipped_old: list[str | Element] = unzip(old)
        unzipped_self: list[str | Element] = unzip(self)
        unzipped_result: list[str | Element] = []
        last_end: int = 0
        for start in index_list:
            unzipped_result.extend(unzipped_self[last_end:start])
            last_end = start + len(unzipped_old)
            unzipped_result.extend(unzipped_new)
        unzipped_result.extend(unzipped_self[last_end:])

        # Merge result
        result_list: list[Element] = []
        char_stk: list[str] = []
        for v in unzipped_result:
            if isinstance(v, str):
                char_stk.append(v)
            else:
                result_list.append(__text_element_class__("".join(char_stk)))
                char_stk = []
                result_list.append(v)
        if char_stk:
            result_list.append(__text_element_class__("".join(char_stk)))
        return self.__class__(result_list)

    def __add__(self, content: MessageChain | list[Element] | Element | str) -> Self:
        if isinstance(content, str):
            content = __text_element_class__(content)
        if isinstance(content, Element):
            content = [content]
        if isinstance(content, MessageChain):
            content = content.content
        return __message_chain_class__(self.content + content)

    def __radd__(self, content: MessageChain | list[Element] | Element | str) -> Self:
        if isinstance(content, str):
            content = __text_element_class__(content)
        if isinstance(content, Element):
            content = [content]
        if isinstance(content, MessageChain):
            content = content.content
        return __message_chain_class__(content + self.content)

    def __iadd__(self, content: MessageChain | list[Element] | Element | str) -> Self:
        if isinstance(content, str):
            content = __text_element_class__(content)
        if isinstance(content, Element):
            content = [content]
        if isinstance(content, MessageChain):
            content = content.content
        self.content.extend(content)
        return self


__message_chain_class__: type[MessageChain] = MessageChain
__text_element_class__: type[Text] = Text
