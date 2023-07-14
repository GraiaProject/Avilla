from typing import TYPE_CHECKING, List

from rich.text import Text

if TYPE_CHECKING:
    from .storage import Storage


class FakeIO:
    def __init__(self, storage: "Storage") -> None:
        self.storage = storage
        self._buffer: List[str] = []

    def isatty(self):
        return True

    def write(self, string: str) -> None:
        self._buffer.append(string)

        # By default, `print` adds a "\n" suffix which results in a buffer
        # flush. You can choose a different suffix with the `end` parameter.
        # If you modify the `end` parameter to something other than "\n",
        # then `print` will no longer flush automatically. However, if a
        # string you are printing contains a "\n", that will trigger
        # a flush after that string has been buffered, regardless of the value
        # of `end`.
        if "\n" in string:
            self.flush()

    def flush(self) -> None:
        self._write_to_storage()
        self._buffer.clear()

    def _write_to_storage(self) -> None:
        self.storage.write_log(
            Text.from_ansi("".join(self._buffer), end="", tab_size=4)
        )
