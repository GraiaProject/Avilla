from collections import defaultdict

from avilla.core.platform import Abstract, Land, Platform

PRIVILEGE_TRANS = defaultdict(
    lambda: "read",
    {
        1: "read",
        2: "manage",
        3: "read+manage",
        4: "speak",
        5: "read+speak",
        6: "manage+speak",
        7: "read+manage+speak",
        8: "live",
        9: "read+live",
        10: "manage+live",
        11: "read+manage+live",
        12: "speak+live",
        13: "read+speak+live",
        14: "manage+speak+live",
        15: "read+manage+speak+live",
    },
)
PLATFORM = Platform(
    Land(
        "qq",
        [{"name": "Tencent"}],
        humanized_name="QQ API",
    ),
    Abstract(
        "qq-api-official",
        [{"name": "Tencent"}],
        humanized_name="QQ API",
    ),
    Abstract(
        "qqapi",
        [{"name": "GraiaProject"}],
        humanized_name="QQ/QQ-Guild Protocol for Avilla, use offical API",
    ),
)
