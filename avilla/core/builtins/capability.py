from ..ryanvk.capability import Capability
from ..ryanvk.descriptor.pull import PullFn
from ..ryanvk.descriptor.query import QuerySchema


class CoreCapability(Capability):
    pull = PullFn()
    query = QuerySchema()
