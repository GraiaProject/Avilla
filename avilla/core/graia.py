import importlib.metadata
import random
import re
from inspect import cleandoc

from loguru import logger

AVILLA_ASCII_LOGO = cleandoc(
    r"""
    [bold]Avilla[/]: a universal backend/framework for effective im development, powered by [blue]Graia Project[/].
        _        _ _ _
       / \__   _(_) | | __ _
      / _ \ \ / / | | |/ _` |
     / ___ \ V /| | | | (_| |
    /_/   \_\_/ |_|_|_|\__,_|
    """
)
AVILLA_ASCII_RAW_LOGO = re.sub(r"\[.*?\]", "", AVILLA_ASCII_LOGO)


if random.choice((True, False)):
    AVILLA_ASCII_LOGO += "\n"
    AVILLA_ASCII_LOGO += "[dim]when will I be able to find a place that can be my second hometown...?[/]"

    # but no matter what, the most important thing for me is always to be with my only loved one.
    # so that the journey will not be lonely.


GRAIA_PROJECT_REPOS = [
    "avilla-core",
    "graia-broadcast",
    "graia-saya",
    "graia-scheduler",
    "graia-ariadne",
    "statv",
    "launart",
    "creart",
    "creart-graia",
    "kayaku",
]


def log_telemetry():
    for telemetry in GRAIA_PROJECT_REPOS:
        try:
            version = importlib.metadata.version(telemetry)
        except Exception:
            version = "unknown / not-installed"
        logger.info(
            f"{telemetry} version: {version}",
            alt=f"[b cornflower_blue]{telemetry}[/] version: [cyan3]{version}[/]",
        )
