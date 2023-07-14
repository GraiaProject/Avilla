from abc import abstractmethod, ABCMeta
from typing import Union, Optional
from dataclasses import dataclass, field, asdict

from graia.amnesia.message.element import Element, Text as BaseText
from rich.console import Console, ConsoleOptions, JustifyMethod, RenderResult
from rich.emoji import Emoji as RichEmoji
from rich.emoji import EmojiVariant
from rich.markdown import Markdown as RichMarkdown
from rich.measure import Measurement, measure_renderables
from rich.style import Style
from rich.text import Text as RichText


class ConsoleElement(Element, metaclass=ABCMeta):
    @property
    @abstractmethod
    def rich(self) -> Union[RichText, RichEmoji, RichMarkdown]:
        pass

    def __str__(self) -> str:
        return str(self.rich)

    def __rich_console__(
            self, console: "Console", options: "ConsoleOptions"
    ) -> "RenderResult":
        yield self.rich

    def __rich_measure__(
            self, console: "Console", options: "ConsoleOptions"
    ) -> Measurement:
        return measure_renderables(console, options, (self.rich,))


class Text(BaseText, ConsoleElement):

    @property
    def rich(self) -> RichText:
        return RichText(self.text, end="")


class Emoji(ConsoleElement):
    name: str

    def __init__(self, name: str):
        self.name = name

    @property
    def rich(self) -> RichEmoji:
        return RichEmoji(self.name)


@dataclass
class Markup(ConsoleElement):
    markup: str
    style: Union[str, Style] = field(default="none")
    emoji: bool = field(default=True)
    emoji_variant: Optional[EmojiVariant] = field(default=None)

    @property
    def rich(self) -> RichText:
        return RichText.from_markup(
            self.markup,
            style=self.style,
            emoji=self.emoji,
            emoji_variant=self.emoji_variant,
            end="",
        )


@dataclass
class Markdown(ConsoleElement):
    markup: str
    code_theme: str = field(default="monokai")
    justify: Optional[JustifyMethod] = field(default=None)
    style: Union[str, Style] = field(default="none")
    hyperlinks: bool = field(default=True)
    inline_code_lexer: Optional[str] = field(default=None)
    inline_code_theme: Optional[str] = field(default=None)

    @property
    def rich(self) -> RichMarkdown:
        return RichMarkdown(**asdict(self))

    def __str__(self) -> str:
        return str(
            RichText.from_markup(
                self.markup,
                style=self.style,
                end="",
            )
        )
