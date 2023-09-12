from dataclasses import dataclass, field
from typing import Optional, Union

from rich.console import JustifyMethod
from rich.emoji import EmojiVariant
from rich.style import Style
from rich.text import Text as RichText

from graia.amnesia.message.element import Element


@dataclass
class Markup(Element):
    markup: str
    style: Union[str, Style] = field(default="none")
    emoji: bool = field(default=True)
    emoji_variant: Optional[EmojiVariant] = field(default=None)

    def __str__(self):
        return f"[$Markup:markup={self.markup}]"


@dataclass
class Markdown(Element):
    markup: str
    code_theme: str = field(default="monokai")
    justify: Optional[JustifyMethod] = field(default=None)
    style: Union[str, Style] = field(default="none")
    hyperlinks: bool = field(default=True)
    inline_code_lexer: Optional[str] = field(default=None)
    inline_code_theme: Optional[str] = field(default=None)

    def __str__(self) -> str:
        return f"[$Markdown:markup={RichText.from_markup(self.markup, style=self.style, end='')}]"
