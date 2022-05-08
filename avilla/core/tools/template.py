import re
from typing import List, Sequence

from graia.amnesia.message import MessageChain
from graia.amnesia.message.element import Element

from avilla.core.elements import Text


def list_get(seq: Sequence, index, default=None):
    return seq[index] if len(seq) - 1 >= index else default


_split = re.compile(r"(?|(\$[a-zA-Z_][a-zA-Z0-9_]*)|(\$[0-9]*))")


class Template:
    template: str

    def __init__(self, template: str) -> None:
        self.template = template

    def split_template(self) -> List[str]:
        return _split.split(self.template)

    def render(self, *args: Element, **kwargs: Element) -> MessageChain:
        patterns = []
        for pattern in self.split_template():
            if pattern:
                if not pattern.startswith("$"):
                    patterns.append(Text(pattern))
                elif re.match(r"\$[a-zA-Z_][a-zA-Z0-9_]*", pattern):
                    patterns.append(kwargs.get(pattern[1:], Text(pattern)))
                elif re.match(r"\$[0-9]*", pattern):
                    patterns.append(list_get(args, int(pattern[1:])))
        return MessageChain(patterns)
