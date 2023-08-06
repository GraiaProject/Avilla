from .chain import MessageChain as MessageChain
from .element import Element as Element
from .element import Text as Text
from .element import Unknown as Unknown
from .formatter import Formatter as Formatter

Element._chain_class = MessageChain
MessageChain._text_class = Text