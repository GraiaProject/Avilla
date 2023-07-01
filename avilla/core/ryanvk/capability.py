from .common.capability import Capability
from .descriptor import PullFn, QuerySchema


class CoreCapability(Capability):
    pull = PullFn()
    query = QuerySchema()
