from .common.capability import Capability
from .fn import FetchFn, PullFn, QuerySchema


class CoreCapability(Capability):
    fetch = FetchFn()
    pull = PullFn()
    query = QuerySchema()