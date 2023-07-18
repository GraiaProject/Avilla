import logging
import sys
import types
from datetime import datetime
from logging import LogRecord
from types import TracebackType
from typing import Any, Callable, Dict, Iterable, List, Optional, Type, Union

from loguru import logger
from loguru._logger import Core
from rich.console import Console, ConsoleRenderable
from rich.logging import RichHandler
from rich.text import Text
from rich.theme import Theme

for lv in Core().levels.values():
    logging.addLevelName(lv.no, lv.name)


class LoguruHandler(logging.Handler):
    def emit(self, record: logging.LogRecord) -> None:
        try:
            level = logger.level(record.levelname).name
        except ValueError:
            level = str(record.levelno)

        frame, depth = logging.currentframe(), 2
        while frame and frame.f_code.co_filename == logging.__file__:
            frame = frame.f_back
            depth += 1

        logger.opt(depth=depth, exception=record.exc_info).log(
            level,
            record.getMessage(),
        )


def highlight(style: str) -> Dict[str, Callable[[Text], Text]]:
    """Add `style` to RichHandler's log text.
    Example:
    ```py
    logger.warning("Sth is happening!", **highlight("red bold"))
    ```
    """

    def highlighter(text: Text) -> Text:
        return Text(text.plain, style=style)

    return {"highlighter": highlighter}


class LoguruRichHandler(RichHandler):
    """
    Interpolate RichHandler in a better way
    Example:
    ```py
    logger.warning("Sth is happening!", style="red bold")
    logger.warning("Sth is happening!", **highlight("red bold"))
    logger.warning("Sth is happening!", alt="[red bold]Sth is happening![/red bold]")
    logger.warning("Sth is happening!", text=Text.from_markup("[red bold]Sth is happening![/red bold]"))
    ```
    """

    def render_message(self, record: LogRecord, message: str) -> "ConsoleRenderable":
        import ast
        import sys

        import devtools
        import executing

        n = devtools.debug(executing.Source.executing(sys._getframe(7)).node)
        if isinstance(n, ast.Call):
            n.args, n.keywords
            
        # alternative time log
        time_format = None if self.formatter is None else self.formatter.datefmt
        time_format = time_format or self._log_render.time_format
        log_time = datetime.fromtimestamp(record.created)
        if callable(time_format):
            time_format(log_time)
        else:
            Text(log_time.strftime(time_format))
        #if not (log_time_display == self._log_render._last_time and self._log_render.omit_repeated_times):
        #    self.console.print(log_time_display, style="log.time")
        #    self._log_render._last_time = log_time_display

        # add extra attrs to record
        extra: dict = getattr(record, "extra", {})
        if "rich" in extra:
            return extra["rich"]
        
        if "style" in extra:
            record.__dict__.update(highlight(extra["style"]))
        elif "highlighter" in extra:
            setattr(record, "highlighter", extra["highlighter"])
        
        if "alt" in extra:
            message = extra["alt"]
            setattr(record, "markup", True)

        if "markup" in extra:
            setattr(record, "markup", extra["markup"])

        if "text" in extra:
            setattr(record, "highlighter", lambda _: extra["text"])

        return super().render_message(record, message)


ExceptionHook = Callable[[Type[BaseException], BaseException, Optional[TracebackType]], Any]


def _loguru_exc_hook(typ: Type[BaseException], val: BaseException, tb: Optional[TracebackType]):
    logger.opt(exception=(typ, val, tb)).error("Exception:")


def _log_formatter(record: dict) -> str:
    """Format log message"""
    name_color = "#289e10"  # 6b189e, c7ecee
    return f" [{name_color}]{{name}}[/{name_color}] | " + " - {message}"


def _time_format(dt: datetime) -> Text:
    t = dt.strftime("%Y-%m-%d %H:%M:%S")
    return Text.from_markup(f"\\[{t}]")

def install(
    rich_console: Optional[Console] = None,
    exc_hook: Optional[ExceptionHook] = _loguru_exc_hook,
    rich_traceback: bool = True,
    tb_ctx_lines: int = 3,
    tb_theme: Optional[str] = None,
    tb_suppress: Iterable[Union[str, types.ModuleType]] = (),
    time_format: Union[str, Callable[[datetime], Text]] = _time_format,
    time_color: str = "#bb6688",
    keywords: Optional[List[str]] = None,
    level: Union[int, str] = 20,
) -> None:
    """Install Rich logging and Loguru exception hook"""
    print(time_format)
    logger.configure(
        handlers=[
            {
                "sink": LoguruRichHandler(
                    console=rich_console
                    or Console(
                        theme=Theme(
                            {
                                "logging.level.success": "green i",
                                "logging.level.debug": "magenta",
                                "logging.level.info": "cyan",
                                "logging.level.warning": "yellow i",
                                "log.time": time_color,
                            }
                        )
                    ),
                    log_time_format=time_format,
                    rich_tracebacks=rich_traceback,
                    tracebacks_show_locals=True,
                    tracebacks_suppress=tb_suppress,
                    tracebacks_extra_lines=tb_ctx_lines,
                    tracebacks_theme=tb_theme,
                    show_time=True,
                    keywords=keywords,
                    omit_repeated_times=True,
                    show_path=False,
                    markup=True,
                ),
                "format": _log_formatter,
                "level": level,
            }
        ]
    )
    if exc_hook is not None:
        sys.excepthook = exc_hook


# install(level=10, time_format="[%m-%d %H:%M:%S]")
