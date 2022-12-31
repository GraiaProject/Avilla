from collections import defaultdict

privilege_trans = defaultdict(lambda: "group_member", {"OWNER": "group_owner", "ADMINISTRATOR": "group_admin"})
privilege_level = defaultdict(lambda: 0, {"OWNER": 2, "ADMINISTRATOR": 1})
