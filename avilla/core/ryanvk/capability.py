from .common.capability import Capability
from .fn import FetchFn, PullFn


class CoreCapability(Capability):
    fetch = FetchFn()
    pull = PullFn()
