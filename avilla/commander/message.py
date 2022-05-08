import re
from typing import Dict, List, Tuple, Type

from graia.amnesia.message import Element, MessageChain

from avilla.commander.utilles import gen_subclass
from avilla.core.elements import Text

ELEMENT_MAPPING: Dict[str, Type[Element]] = {i.__name__: i for i in gen_subclass(Element)}


def chain_from_mapping_string(string: str, mapping: Dict[str, Element]) -> "MessageChain":
    """从映射字符串与映射字典的元组还原消息链.

    Args:
        string (str): 映射字符串
        mapping (Dict[int, Element]): 映射字典.

    Returns:
        MessageChain: 构建的消息链
    """
    elements: List[Element] = []
    for x in re.split("(\x02\\d+_\\w+\x03)", string):
        if x:
            if x[0] == "\x02" and x[-1] == "\x03":
                index, class_name = x[1:-1].split("_")
                if not isinstance(mapping[index], ELEMENT_MAPPING[class_name]):
                    raise ValueError("Validation failed: not matching element type!")
                elements.append(mapping[index])
            else:
                elements.append(Text(x))
    chain = MessageChain(elements)
    return chain


def chain_to_mapping_str(
    message_chain: MessageChain,
) -> Tuple[str, Dict[str, Element]]:
    """转换消息链为映射字符串与映射字典的元组.

    Returns:
        Tuple[str, Dict[str, Element]]: 生成的映射字符串与映射字典的元组
    """
    elem_mapping: Dict[str, Element] = {}
    elem_str_list: List[str] = []
    for i, elem in enumerate(message_chain.content):
        if not isinstance(elem, Text):
            elem_mapping[str(i)] = elem
            elem_str_list.append(f"\x02{i}_{elem.__class__.__name__}\x03")
        else:
            elem_str_list.append(elem.text)
    return "".join(elem_str_list), elem_mapping
