from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Any

def escape(text: str) -> str:
    return text.replace("\"", "&quot;").replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")

def unescape(text: str) -> str:
    return text.replace("&quot;", "\"").replace("&amp;", "&").replace("&lt;", "<").replace("&gt;", ">")


@dataclass
class Element:
    type: str
    attrs: dict[str, Any] = field(default_factory=dict)
    children: list['Element'] = field(default_factory=list)
    source: str | None = None
    

tag_pat = re.compile(r"<!--[\s\S]*?-->|<(/?)([^!\s>/]*)([^>]*?)\s*(/?)>")
attr_pat = re.compile(r"([^\s=]+)(?:=\"([^\"]*)\"|='([^']*)')?", re.S)

@dataclass
class Token:
    type: str
    close: str
    empty: str
    attrs: dict[str, Any]
    source: str


def parse(src: str):
    tokens: list[Token | Element] = []

    def push_text(text: str):
        if text:
            tokens.append(Element("text", {"text": text}))

    def parse_content(source: str):
        push_text(unescape(source))

    while tag_map := tag_pat.search(src):
        parse_content(src[:tag_map.start()])
        src = src[tag_map.end():]
        if tag_map.group(0).startswith("<!--"):
            continue
        close, tag, attr_str, empty = tag_map.groups()
        tkn = Token(
            type=tag or "template",
            close=close,
            empty=empty,
            attrs={},
            source=tag_map.group(0)
        )
        while attr_map := attr_pat.search(attr_str):
            key, value1, value2 = attr_map.groups()
            value = value1 or value2
            if value:
                tkn.attrs[key] = unescape(value)
            elif key.startswith("no-"):
                tkn.attrs[key] = False
            else:
                tkn.attrs[key] = True
            attr_str = attr_str[attr_map.end():]
        tokens.append(tkn)

    parse_content(src)

    stack = [Element("template")]

    def rollback(i: int):
        while i:
            child = stack.pop(0)
            source = stack[0].children.pop(-1)
            stack[0].children.append(Element("text", {"text": source}))
            stack[0].children.extend(child.children)
            i -= 1

    for tkn in tokens:
        if isinstance(tkn, Element):
            stack[0].children.append(tkn)
        elif tkn.close:
            index = 0
            while index < len(stack) and stack[index].type != tkn.type:
                index += 1
            if index == len(stack):
                stack[0].children.append(Element("text", {"text": tkn.source}))
            else:
                rollback(index)
                elm = stack.pop(0)
                elm.source = None
        else:
            elm = Element(tkn.type, tkn.attrs)
            stack[0].children.append(elm)
            if not tkn.empty:
                elm.source = tkn.source
                stack.insert(0, elm)

    rollback(len(stack) - 1)
    return stack[0].children
