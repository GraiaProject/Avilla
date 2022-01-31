import copy
from dataclasses import dataclass
from datetime import datetime
from typing import TYPE_CHECKING, Iterable, List, Optional, Type, TypeVar, Union

from pydantic import BaseModel  # pylint: ignore

from avilla.core.selectors import entity
from avilla.core.selectors import mainline as mainline_selector
from avilla.core.selectors import message as message_selector


@dataclass
class Message:
    id: str
    mainline: mainline_selector
    sender: entity
    content: "MessageChain"
    time: datetime
    reply: Optional["message_selector"] = None

    def to_selector(self) -> "message_selector":
        return message_selector.mainline[self.mainline]._[self.id]


class Element:
    def asDisplay(self) -> str:
        return ""

    @classmethod
    def get_ability_id(cls) -> str:
        return f"msg_element::{cls.__name__}"


class MessageChain:
    """即 "消息链", 被用于承载整个消息内容的数据结构, 包含有一有序列表, 包含有继承了 Element 的各式类实例.
    Example:
        1. 你可以使用 `MessageChain` 方法创建一个消息链:
            ``` python
            MessageChain([
                Text("这是盛放在这个消息链中的一个 Text 元素")
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
            print(message.has(Notice))
            # 使用 in 运算符也可以
            print(Notice in message)
            ```
        7. 可以使用 `MessageChain.get` 方法获取消息链中的所有特定类型的元素:
            ``` python
            print(message.get(Image)) # -> List[Image]
            # 使用类似取出列表中元素的形式也可以:
            print(message[Image]) # -> List[Image]
            ```
        8. 使用 `MessageChain.asDisplay` 方法可以获取到字符串形式表示的消息, 至于字面意思, 看示例:
            ``` python
            print(MessageChain([
                Text("text"), Notice(123, display="某人"), Image(...)
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
        14. `MessageChain.asMerged` 方法可以将消息链中相邻的 Text 元素合并为一个 Text 元素.
        15. 你可以通过一个分片实例取项, 这个分片的 `start` 和 `end` 的 Type Annotation 都是 `Optional[MessageIndex]`:
            ``` python
            message = MessageChain([
                Text("123456789"), Notice(123), Text("3423")
            ])
            message.asMerged()[(0, 12):] # => [Notice(123), Text("3423")]
            ```
    """

    content: List[Element]

    def __init__(self, elements: List[Element]):
        """从传入的序列(可以是元组 tuple, 也可以是列表 list) 创建消息链.
        Args:
            elements (List[T]): 包含且仅包含消息元素的序列
        Returns:
            MessageChain: 以传入的序列作为所承载消息的消息链
        """
        self.content = elements

    def has(self, element_class: Type[Element]) -> bool:
        """判断消息链中是否含有特定类型的消息元素
        Args:
            element_class (T): 需要判断的消息元素的类型, 例如 "Text", "Notice", "Image" 等.
        Returns:
            bool: 判断结果
        """
        return element_class in [type(i) for i in self.content]

    def get(self, element_class: Type[Element]) -> List[Element]:
        """获取消息链中所有特定类型的消息元素
        Args:
            element_class (T): 指定的消息元素的类型, 例如 "Text", "Notice", "Image" 等.
        Returns:
            List[T]: 获取到的符合要求的所有消息元素; 另: 可能是空列表([]).
        """
        return [i for i in self.content if type(i) is element_class]

    def get_one(self, element_class: Type[Element], index: int) -> Element:
        """获取消息链中第 index + 1 个特定类型的消息元素
        Args:
            element_class (Type[Element]): 指定的消息元素的类型, 例如 "Text", "Notice", "Image" 等.
            index (int): 索引, 从 0 开始数
        Returns:
            T: 消息链第 index + 1 个特定类型的消息元素
        """
        return self.get(element_class)[index]

    if TYPE_CHECKING:
        E = TypeVar("E", bound=Element)

    def get_first(self, element_class: "Type[E]") -> "E":
        """获取消息链中第 1 个特定类型的消息元素
        Args:
            element_class (Type[Element]): 指定的消息元素的类型, 例如 "Text", "Notice", "Image" 等.
        Returns:
            T: 消息链第 1 个特定类型的消息元素
        """
        return self.get_one(element_class, 0)  # type: ignore

    def as_display(self) -> str:
        """获取以字符串形式表示的消息链, 且趋于通常你见到的样子.
        Returns:
            str: 以字符串形式表示的消息链
        """
        return "".join(i.asDisplay() for i in self.content)

    @classmethod
    def join(cls, *chains: "MessageChain") -> "MessageChain":
        """拼接参数中给出的所有消息链
        Returns:
            MessageChain: 拼接结果
        """
        return cls(sum([list(i.content) for i in chains], []))

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
        from .elements import Text

        result = copy.copy(self.content)
        if item.start:
            first_slice = result[item.start[0] :]
            if item.start[1] is not None and first_slice:  # text slice
                if not isinstance(first_slice[0], Text):
                    if not ignore_text_index:
                        raise TypeError(
                            "the sliced chain does not starts with a Text: {}".format(first_slice[0])
                        )
                    else:
                        result = first_slice
                else:
                    final_text = first_slice[0].text[item.start[1] :]
                    result = [
                        *([Text(final_text)] if final_text else []),
                        *first_slice[1:],
                    ]
            else:
                result = first_slice
        if item.stop:
            first_slice = result[: item.stop[0]]
            if item.stop[1] is not None and first_slice:  # text slice
                if not isinstance(first_slice[-1], Text):
                    raise TypeError("the sliced chain does not ends with a Text: {}".format(first_slice[-1]))
                final_text = first_slice[-1].text[: item.stop[1]]  # type: ignore
                result = [
                    *first_slice[:-1],
                    *([Text(final_text)] if final_text else []),
                ]
            else:
                result = first_slice
        return MessageChain(result)

    def as_merged(self) -> "MessageChain":
        """合并相邻的 Text 项, 并返回一个新的消息链实例
        Returns:
            MessageChain: 得到的新的消息链实例, 里面不应存在有任何的相邻的 Text 元素.
        """
        from .elements import Text

        result = []

        texts = []
        for i in self.content:
            if not isinstance(i, Text):
                if texts:
                    result.append(Text("".join(texts)))
                    texts.clear()  # 清空缓存
                result.append(i)
            else:
                texts.append(i.text)
        else:
            if texts:
                result.append(Text("".join(texts)))
                texts.clear()  # 清空缓存
        return MessageChain(type(self.content)(result))  # 维持 Mutable

    def exclude(self, *types: Type[Element]) -> "MessageChain":
        """将除了在给出的消息元素类型中符合的消息元素重新包装为一个新的消息链
        Args:
            *types (Type[Element]): 将排除在外的消息元素类型
        Returns:
            MessageChain: 返回的消息链中不包含参数中给出的消息元素类型
        """
        return MessageChain([i for i in self.content if type(i) not in types])

    def include(self, *types: Type[Element]) -> "MessageChain":
        """将只在给出的消息元素类型中符合的消息元素重新包装为一个新的消息链
        Args:
            *types (Type[Element]): 将只包含在内的消息元素类型
        Returns:
            MessageChain: 返回的消息链中只包含参数中给出的消息元素类型
        """
        return MessageChain([i for i in self.content if type(i) in types])

    def split(self, pattern: str, raw_string: bool = False) -> List["MessageChain"]:
        """和 `str.split` 差不多, 提供一个字符串, 然后返回分割结果.
        Returns:
            List["MessageChain"]: 分割结果, 行为和 `str.split` 差不多.
        """
        from .elements import Text

        result: List["MessageChain"] = []
        tmp = []
        for element in self.content:
            if isinstance(element, Text):
                split_result = element.text.split(pattern)
                for index, split_str in enumerate(split_result):
                    if tmp and index > 0:
                        result.append(MessageChain(tmp))
                        tmp = []
                    if split_str or raw_string:
                        tmp.append(Text(split_str))
            else:
                tmp.append(element)
        else:
            if tmp:
                result.append(MessageChain(tmp))
                tmp = []
        return result

    def __repr__(self) -> str:
        return f"MessageChain({repr(self.content)})"

    def __iter__(self) -> Iterable[Element]:
        yield from self.content

    def startswith(self, string: str) -> bool:
        from .elements import Text

        if not self.content or type(self.content[0]) is not Text:
            return False
        return self.content[0].text.startswith(string)

    def endswith(self, string: str) -> bool:
        from .elements import Text

        if not self.content or type(self.content[-1]) is not Text:
            return False
        return self.content[-1].text.endswith(string)  # type: ignore
