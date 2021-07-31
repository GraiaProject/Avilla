from __future__ import annotations

import copy
from typing import Iterable, List, NoReturn, Optional, Sequence, Tuple, Type, Union

from .element import Element
from pydantic import BaseModel

MessageIndex = Tuple[int, Optional[int]]


class MessageChain(BaseModel):
    """即 "消息链", 被用于承载整个消息内容的数据结构, 包含有一有序列表, 包含有继承了 Element 的各式类实例.
    Example:
        1. 你可以使用 `MessageChain.create` 方法创建一个消息链:
            ``` python
            MessageChain.create([
                PlainText("这是盛放在这个消息链中的一个 PlainText 元素")
            ])
            ```
        2. 你可以使用 `MessageChain.isImmutable` 方法判定消息链的可变型:
            ``` python
            print(message.isImmutable()) # 监听器获取到的消息链默认为 False.
            ```
        3. 你可以使用 `MessageChain.asMutable` 和 `MessageChain.asImmutable` 方法分别获得可变与不可变的消息链.
        4. 你可以使用 `MessageChain.isSendable` 方法检查消息链是否可以被 **完整无误** 的发送.
        5. 使用 `MessageChain.asSendable` 方法, 将自动过滤原消息链中的无法发送的元素, 并返回一个新的, 可被发送的消息链.
        6. `MessageChain.has` 方法可用于判断特定的元素类型是否存在于消息链中:
            ``` python
            print(message.has(At))
            # 使用 in 运算符也可以
            print(At in message)
            ```
        7. 可以使用 `MessageChain.get` 方法获取消息链中的所有特定类型的元素:
            ``` python
            print(message.get(Image)) # -> List[Image]
            # 使用类似取出列表中元素的形式也可以:
            print(message[Image]) # -> List[Image]
            ```
        8. 使用 `MessageChain.asDisplay` 方法可以获取到字符串形式表示的消息, 至于字面意思, 看示例:
            ``` python
            print(MessageChain.create([
                PlainText("text"), At(123, display="某人"), Image(...)
            ]).asDisplay()) # -> "text@某人 [图片]"
            ```
        9. 使用 `MessageChain.join` 方法可以拼接多个消息链:
            ``` python
            MessageChain.join(
                message1, message2, message3, ...
            ) # -> MessageChain
            ```
        10. `MessageChain.plusWith` 方法将在现有的基础上将另一消息链拼接到原来实例的尾部, 并生成, 返回新的实例; 该方法不改变原有和传入的实例.
        11. `MessageChain.plus` 方法将在现有的基础上将另一消息链拼接到原来实例的尾部; 该方法更改了原有的实例, 并要求 `isMutable` 方法返回 `True` 才可以执行.
        14. `MessageChain.asMerged` 方法可以将消息链中相邻的 PlainText 元素合并为一个 PlainText 元素.
        15. 你可以通过一个分片实例取项, 这个分片的 `start` 和 `end` 的 Type Annotation 都是 `Optional[MessageIndex]`:
            ``` python
            message = MessageChain.create([
                PlainText("123456789"), At(123), PlainText("3423")
            ])
            message.asMerged()[(0, 12):] # => [At(123), PlainText("3423")]
            ```
    """

    __root__: Sequence[Element]

    @classmethod
    def create(cls, elements: Sequence[Element]) -> "MessageChain":
        """从传入的序列(可以是元组 tuple, 也可以是列表 list) 创建消息链.
        Args:
            elements (Sequence[T]): 包含且仅包含消息元素的序列
        Returns:
            MessageChain: 以传入的序列作为所承载消息的消息链
        """
        return cls(__root__=elements)

    @property
    def isImmutable(self) -> bool:
        """判断消息链是否不可变
        Returns:
            bool: 判断结果, `True` 为不可变, `False` 为可变
        """
        return isinstance(self.__root__, tuple)

    def asMutable(self) -> "MessageChain":
        """将消息链转换为可变形态的消息链
        Returns:
            MessageChain: 内部消息结构可变的消息链
        """
        return MessageChain(__root__=list(self.__root__))

    def asImmutable(self) -> "MessageChain":
        """将消息链转换为不可变形态的消息链
        Returns:
            MessageChain: 内部消息结构不可变的消息链
        """
        return MessageChain(__root__=tuple(self.__root__))

    def has(self, element_class: Element) -> bool:
        """判断消息链中是否含有特定类型的消息元素
        Args:
            element_class (T): 需要判断的消息元素的类型, 例如 "PlainText", "At", "Image" 等.
        Returns:
            bool: 判断结果
        """
        return element_class in [type(i) for i in self.__root__]

    def get(self, element_class: Element) -> List[Element]:
        """获取消息链中所有特定类型的消息元素
        Args:
            element_class (T): 指定的消息元素的类型, 例如 "PlainText", "At", "Image" 等.
        Returns:
            List[T]: 获取到的符合要求的所有消息元素; 另: 可能是空列表([]).
        """
        return [i for i in self.__root__ if type(i) is element_class]

    def getOne(self, element_class: Element, index: int) -> Element:
        """获取消息链中第 index + 1 个特定类型的消息元素
        Args:
            element_class (Type[Element]): 指定的消息元素的类型, 例如 "PlainText", "At", "Image" 等.
            index (int): 索引, 从 0 开始数
        Returns:
            T: 消息链第 index + 1 个特定类型的消息元素
        """
        return self.get(element_class)[index]

    def getFirst(self, element_class: Element) -> Element:
        """获取消息链中第 1 个特定类型的消息元素
        Args:
            element_class (Type[Element]): 指定的消息元素的类型, 例如 "PlainText", "At", "Image" 等.
        Returns:
            T: 消息链第 1 个特定类型的消息元素
        """
        return self.getOne(element_class, 0)

    def asDisplay(self) -> str:
        """获取以字符串形式表示的消息链, 且趋于通常你见到的样子.
        Returns:
            str: 以字符串形式表示的消息链
        """
        return "".join(i.asDisplay() for i in self.__root__)

    @classmethod
    def join(cls, *chains: "MessageChain") -> "MessageChain":
        """拼接参数中给出的所有消息链
        Returns:
            MessageChain: 拼接结果
        """
        return cls.create(sum([list(i.__root__) for i in chains], []))

    def plusWith(self, *chains: "MessageChain") -> "MessageChain":
        """在现有的基础上将另一消息链拼接到原来实例的尾部, 并生成, 返回新的实例.
        Returns:
            MessageChain: 拼接结果
        """
        return self.create(sum([list(i.__root__) for i in chains], self.__root__))

    def plus(self, *chains: "MessageChain") -> NoReturn:
        """在现有的基础上将另一消息链拼接到原来实例的尾部
        Raises:
            ValueError: 原有的消息链不可变, 需要转为可变形态.
        Returns:
            NoReturn: 本方法无返回.
        """
        if self.isImmutable:
            raise ValueError("this chain is not mutable")
        for i in chains:
            self.__root__.extend(list(i.__root__))

    __contains__ = has

    def __getitem__(self, item: Union[Type[Element], slice]):
        if isinstance(item, slice):
            return self.subchain(item)
        elif issubclass(item, Element):
            return self.get(item)
        else:
            raise NotImplementedError("{0} is not allowed for item getting".format(type(item)))

    def subchain(self, item: slice, ignore_text_index: bool = False) -> "MessageChain":
        """对消息链执行分片操作
        Args:
            item (slice): 这个分片的 `start` 和 `end` 的 Type Annotation 都是 `Optional[MessageIndex]`
        Raises:
            TypeError: TextIndex 取到了错误的位置
        Returns:
            MessageChain: 分片后得到的新消息链, 绝对是原消息链的子集.
        """
        from ..builtins.elements import PlainText

        result = copy.copy(self.__root__)
        if item.start:
            first_slice = result[item.start[0] :]
            if item.start[1] is not None and first_slice:  # text slice
                if not isinstance(first_slice[0], PlainText):
                    if not ignore_text_index:
                        raise TypeError("the sliced chain does not starts with a PlainText: {}".format(first_slice[0]))
                    else:
                        result = first_slice
                else:
                    final_text = first_slice[0].text[item.start[1] :]
                    result = [
                        *([PlainText(final_text)] if final_text else []),
                        *first_slice[1:],
                    ]
            else:
                result = first_slice
        if item.stop:
            first_slice = result[: item.stop[0]]
            if item.stop[1] is not None and first_slice:  # text slice
                if not isinstance(first_slice[-1], PlainText):
                    raise TypeError("the sliced chain does not ends with a PlainText: {}".format(first_slice[-1]))
                final_text = first_slice[-1].text[: item.stop[1]]
                result = [
                    *first_slice[:-1],
                    *([PlainText(final_text)] if final_text else []),
                ]
            else:
                result = first_slice
        return MessageChain.create(result)

    def asMerged(self) -> "MessageChain":
        """合并相邻的 PlainText 项, 并返回一个新的消息链实例
        Returns:
            MessageChain: 得到的新的消息链实例, 里面不应存在有任何的相邻的 PlainText 元素.
        """
        from ..builtins.elements import PlainText

        result = []

        PlainText = []
        for i in self.__root__:
            if not isinstance(i, PlainText):
                if PlainText:
                    result.append(PlainText("".join(PlainText)))
                    PlainText.clear()  # 清空缓存
                result.append(i)
            else:
                PlainText.append(i.text)
        else:
            if PlainText:
                result.append(PlainText("".join(PlainText)))
                PlainText.clear()  # 清空缓存
        return MessageChain.create(type(self.__root__)(result))  # 维持 Mutable

    def exclude(self, *types: Type[Element]) -> MessageChain:
        """将除了在给出的消息元素类型中符合的消息元素重新包装为一个新的消息链
        Args:
            *types (Type[Element]): 将排除在外的消息元素类型
        Returns:
            MessageChain: 返回的消息链中不包含参数中给出的消息元素类型
        """
        return self.create(type(self.__root__)([i for i in self.__root__ if type(i) not in types]))

    def include(self, *types: Type[Element]) -> MessageChain:
        """将只在给出的消息元素类型中符合的消息元素重新包装为一个新的消息链
        Args:
            *types (Type[Element]): 将只包含在内的消息元素类型
        Returns:
            MessageChain: 返回的消息链中只包含参数中给出的消息元素类型
        """
        return self.create(type(self.__root__)([i for i in self.__root__ if type(i) in types]))

    def split(self, pattern: str, raw_string: bool = False) -> List["MessageChain"]:
        """和 `str.split` 差不多, 提供一个字符串, 然后返回分割结果.
        Returns:
            List["MessageChain"]: 分割结果, 行为和 `str.split` 差不多.
        """
        from ..builtins.elements import PlainText

        result: List["MessageChain"] = []
        tmp = []
        for element in self.__root__:
            if isinstance(element, PlainText):
                split_result = element.text.split(pattern)
                for index, split_str in enumerate(split_result):
                    if tmp and index > 0:
                        result.append(MessageChain.create(tmp))
                        tmp = []
                    if split_str or raw_string:
                        tmp.append(PlainText(split_str))
            else:
                tmp.append(element)
        else:
            if tmp:
                result.append(MessageChain.create(tmp))
                tmp = []
        return result

    def __repr__(self) -> str:
        return f"MessageChain({repr(self.__root__)})"

    def __iter__(self) -> Iterable[Element]:
        yield from self.__root__

    def startswith(self, string: str) -> bool:
        from ..builtins.elements import PlainText

        if not self.__root__ or type(self.__root__[0]) is not PlainText:
            return False
        return self.__root__[0].text.startswith(string)

    def endswith(self, string: str) -> bool:
        from ..builtins.elements import PlainText

        if not self.__root__ or type(self.__root__[-1]) is not PlainText:
            return False
        return self.__root__[-1].text.endswith(string)
