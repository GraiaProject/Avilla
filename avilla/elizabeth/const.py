from collections import defaultdict

from avilla.core.platform import Abstract, Land, Platform

PRIVILEGE_TRANS = defaultdict(lambda: "group_member", {"OWNER": "group_owner", "ADMINISTRATOR": "group_admin"})
PRIVILEGE_LEVEL = defaultdict(lambda: 0, {"OWNER": 2, "ADMINISTRATOR": 1})
LAND = Land("qq", [{"name": "Tencent"}], humanized_name="QQ")
PLATFORM = Platform(
    LAND,
    Abstract(
        protocol="mirai-api-http",
        maintainers=[{"name": "royii"}],
        humanized_name="mirai-api-http protocol",
    ),
    Land(
        "elizabeth",
        [{"name": "GraiaProject"}],
        humanized_name="Elizabeth - mirai-api-http for avilla",
    ),
)
