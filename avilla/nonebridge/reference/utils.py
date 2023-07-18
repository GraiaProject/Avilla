"""OneBot 辅助函数。

FrontMatter:
    sidebar_position: 3
    description: onebot.utils 模块
"""

import re
from base64 import b64encode
from io import BytesIO
from pathlib import Path
from typing import Iterable, Optional, Tuple, Union

from nonebot.utils import escape_tag

RICH_REGEX = (
    r"\[(?P<type>[a-zA-Z0-9-_.]+)" r"(?::" r"(?P<params>" r"(?:" r"[a-zA-Z0-9-_.]+=[^,\]]*,?" r")*" r")" r")?" r"\]"
)


def rich_escape(s: str, escape_comma: bool = True) -> str:
    """对字符串进行富文本转义。

    参数:
        s: 需要转义的字符串
        escape_comma: 是否转义逗号（`,`）。
    """
    s = s.replace("&", "&amp;").replace("[", "&#91;").replace("]", "&#93;")
    if escape_comma:
        s = s.replace(",", "&#44;")
    return s


def rich_unescape(s: str) -> str:
    """对字符串进行富文本去转义。

    参数:
        s: 需要去转义的字符串
    """
    return s.replace("&#44;", ",").replace("&#91;", "[").replace("&#93;", "]").replace("&amp;", "&")


def iter_rich_message(msg: str) -> Iterable[Tuple[str, str]]:
    text_begin = 0
    for segment in re.finditer(RICH_REGEX, msg):
        if pre_text := msg[text_begin : segment.pos + segment.start()]:
            yield "text", pre_text

        text_begin = segment.pos + segment.end()
        yield segment["type"], segment["params"].rstrip(",")

    if trailing_text := msg[text_begin:]:
        yield "text", trailing_text


def highlight_rich_message(msg: str) -> Iterable[str]:
    for type, params in iter_rich_message(msg):
        if type == "text":
            yield escape_tag(rich_unescape(params))
        else:
            seg_str = f"[{type}{f':{rich_unescape(params)}' if params else ''}]"
            yield f"<le>{escape_tag(seg_str)}</le>"


def get_auth_bearer(access_token: Optional[str] = None) -> Optional[str]:
    if not access_token:
        return None
    scheme, _, param = access_token.partition(" ")
    return param if scheme.lower() in {"bearer", "token"} else None


def b2s(b: Optional[bool]) -> Optional[str]:
    """转换布尔值为字符串。"""
    return b if b is None else str(b).lower()


def f2s(file: Union[str, bytes, BytesIO, Path]) -> str:
    if isinstance(file, BytesIO):
        file = file.getvalue()
    if isinstance(file, bytes):
        file = f"base64://{b64encode(file).decode()}"
    elif isinstance(file, Path):
        file = file.resolve().as_uri()
    return file


def truncate(s: str, length: int = 70, kill_words: bool = True, end: str = "...") -> str:
    """将给定字符串截断到指定长度。

    参数:
        s: 需要截取的字符串
        length: 截取长度
        kill_words: 是否不保留完整单词
        end: 截取字符串的结尾字符

    返回:
        截取后的字符串
    """
    if len(s) <= length:
        return s

    if kill_words:
        return s[: length - len(end)] + end

    result = s[: length - len(end)].rsplit(maxsplit=1)[0]
    return result + end
