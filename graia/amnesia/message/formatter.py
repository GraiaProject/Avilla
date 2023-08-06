from __future__ import annotations

import re
from collections.abc import Sequence
from typing import ClassVar

from graia.amnesia.message import MessageChain
from graia.amnesia.message.element import Element


class Formatter:
    format_string: str
    __message_chain_class__: ClassVar[type[MessageChain]] = MessageChain

    def __init__(self, format_string: str) -> None:
        self.format_string = format_string

    @classmethod
    def ensure_element(cls, obj: str | Element) -> Element:
        return cls.__message_chain_class__._text_class(obj) if isinstance(obj, str) else obj

    @classmethod
    def extract_chain(cls, obj: Element | MessageChain | str | Sequence[Element]) -> list[Element]:
        if isinstance(obj, MessageChain):
            return obj.content
        if isinstance(obj, str):
            obj = cls.ensure_element(obj)
        if isinstance(obj, Element):
            return [obj]
        if isinstance(obj, Sequence):
            return list(obj)

    def format(self, *o_args: Element | MessageChain | str, **o_kwargs: Element | MessageChain | str) -> MessageChain:
        args: list[list[Element]] = [self.extract_chain(e) for e in o_args]
        kwargs: dict[str, list[Element]] = {k: self.extract_chain(e) for k, e in o_kwargs.items()}

        args_mapping: dict[str, list[Element]] = {f"\x02{index}\x02": chain for index, chain in enumerate(args)}
        kwargs_mapping: dict[str, list[Element]] = {f"\x03{key}\x03": chain for key, chain in kwargs.items()}

        result = self.format_string.format(*args_mapping, **{k: f"\x03{k}\x03" for k in kwargs})

        chain_list: list[Element] = []

        for i in re.split("([\x02\x03][\\d\\w]+[\x02\x03])", result):
            if match := re.fullmatch("(?P<header>[\x02\x03])(?P<content>\\w+)(?P=header)", i):
                header = match["header"]
                full: str = match[0]
                if header == "\x02":  # from args
                    chain_list.extend(args_mapping[full])
                else:  # \x03, from kwargs
                    chain_list.extend(kwargs_mapping[full])
            else:
                chain_list.append(self.ensure_element(i))
        return MessageChain(chain_list).merge()
