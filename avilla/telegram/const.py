from avilla.core.platform import Abstract, Land, Platform

LAND = Land("telegram", [{"name": "Telegram"}], humanized_name="Telegram")
PLATFORM = Platform(
    LAND,
    # TODO: rewrite Abstract
    Abstract(
        protocol="python-telegram-bot",
        maintainers=[{"name": "python-telegram-bot"}],
        humanized_name="python-telegram-bot",
    ),
    Land(
        "telegram",
        [{"name": "GraiaProject"}],
        humanized_name="Telegram adapter for Avilla",
    ),
)
