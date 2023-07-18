from avilla.core.platform import Abstract, Land, Platform

PLATFORM = Platform(
    Land(
        "qqguild",
        [{"name": "Tencent"}],
        humanized_name="QQ Guild",
    ),
    Abstract(
        "qqguild",
        [{"name": "Tencent"}],
        humanized_name="QQ Guild",
    ),
    Land(
        "qqguild",
        [{"name": "GraiaProject"}],
        humanized_name="QQ Guild Protocol for Avilla",
    ),
)
