import inspect
from typing import TypeVar, Union, Type, Dict

AnyIP = r"(\d+)\.(\d+)\.(\d+)\.(\d+)"
AnyDigit = r"(\d+)"
AnyStr = r"(.+)"
AnyUrl = r"(http[s]?://.+)"
Bool = r"(True|False)"

NonTextElement = TypeVar("NonTextElement")
MessageChain = TypeVar("MessageChain")
Argument_T = Union[str, Type[NonTextElement]]


class Args:
    args: Dict[str, Argument_T]
    _default: Dict[str, Union[str, NonTextElement]]
    empty: bool = False

    def __init__(self, **kwargs):
        self.args = {k: v for k, v in kwargs.items() if k not in ('name', 'type')}
        self._default = {}
        if not self.args:
            self.empty = True

    def default(self, **kwargs):
        self._default = {k: v for k, v in kwargs.items() if k not in ('name', 'type')}
        return self

    def check(self, keyword: str):
        if keyword in self._default:
            if self._default[keyword] is None:
                return inspect.Signature.empty
            return self._default[keyword]

    def params(self, sep: str = " "):
        argument_string = ""
        i = 0
        length = len(self.args)
        for k, v in self.args.items():
            arg = f"<{k}"
            if not isinstance(v, str):
                arg += f": Type_{v.__name__}"
            if k in self._default:
                default = self._default[k]
                if default is None:
                    arg += " default: Empty"
                elif isinstance(default, str):
                    arg += f" default: {default}"
                else:
                    arg += f" default: Type_{default.__name__}"
            argument_string += arg + ">"
            i += 1
            if i != length:
                argument_string += sep
        return argument_string

    def __iter__(self):
        for k, v in self.args.items():
            yield k, v

    def __len__(self):
        return len(self.args)

    def __repr__(self):
        if self.empty:
            return "Empty"
        repr_string = ""
        for k, v in self.args.items():
            text = f"'{k}': {v}"
            if k in self._default:
                text += f" default={self._default[k]}"
            repr_string += text + ",\n"
        return "\n" + repr_string + ""
