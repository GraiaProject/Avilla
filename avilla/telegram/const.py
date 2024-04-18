from avilla.core.platform import Abstract, Land, Platform

LAND = Land("telegram", [{"name": "Telegram"}], humanized_name="Telegram")
PLATFORM = Platform(
    LAND,
    Abstract(
        protocol="telegram-bot-api",
        maintainers=[{"name": "Telegram"}],
        humanized_name="Telegram Bot API",
    ),
    Land(
        "telegram",
        [{"name": "GraiaProject"}],
        humanized_name="Telegram adapter for Avilla",
    ),
)
