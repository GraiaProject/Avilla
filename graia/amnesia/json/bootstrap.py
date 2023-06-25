CURRENT_BACKEND = None

try:
    import json
except ImportError:
    pass
else:
    from .backend.std import BACKEND_INSTANCE

    CURRENT_BACKEND = BACKEND_INSTANCE

try:
    import ujson
except ImportError:
    pass
else:
    from .backend.ujson import BACKEND_INSTANCE

    CURRENT_BACKEND = BACKEND_INSTANCE

try:
    import orjson
except ImportError:
    pass
else:
    from .backend.orjson import BACKEND_INSTANCE

    CURRENT_BACKEND = BACKEND_INSTANCE
