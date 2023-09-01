from avilla.core.platform import Abstract, Land, Platform

LAND = Land("telegram", [{"name": "Telegram"}], humanized_name="Telegram")
PLATFORM = Platform(
    LAND,
    Abstract(
        protocol="python-telegram-bot",
        maintainers=[],
        humanized_name="python-telegram-bot",
    ),
    Land(
        "telegram",
        [{"name": "GraiaProject"}],
        humanized_name="",
    ),
)
