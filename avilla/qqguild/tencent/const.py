from avilla.core.platform import Abstract, Land, Platform

PLATFORM = Platform(
    Land(
        "qqguild",
        [{"name": "Tencent"}],
        humanized_name="QQ Guild",
    ),
    Abstract(
        "qqguild-official",
        [{"name": "Tencent"}],
        humanized_name="QQ Guild",
    ),
    Abstract(
        "qqguild/tencent",
        [{"name": "GraiaProject"}],
        humanized_name="QQ Guild Protocol for Avilla, use offical API",
    ),
)
