from typing import TYPE_CHECKING, Any, Callable, Dict, Generic, Optional

from immutables import Map

from avilla.core.typing import T_Protocol

if TYPE_CHECKING:
    from avilla.core.protocol import BaseProtocol

T_SubBus = Callable[["BaseProtocol", Dict[str, Any]], Any]


class OverrideException(Exception):
    pass


class OverrideBus(Generic[T_Protocol]):
    "specially for [BaseProtocol.ensure_execution]"
    param_receiver: Callable
    overrides: Dict[Map, Callable]
    pattern: Dict[str, T_SubBus]
    default_factories: Dict[str, Callable]

    def __init__(
        self,
        param_receiver: Callable,
        pattern: Dict[str, T_SubBus],
        default_factories: Optional[Dict[str, Callable]] = None,
    ) -> None:
        self.param_receiver = param_receiver
        self.pattern = pattern
        self.default_factories = default_factories or {}
        self.overrides = {}

    def __call__(self, protocol: T_Protocol, *args: Any, **kwargs: Any) -> Any:
        params = self.param_receiver(*args, **kwargs)
        current_sign = Map(
            **{name: subbus(protocol, params) for name, subbus in self.pattern.items()}
        )
        selected = self.overrides.get(current_sign)
        if selected is None:
            raise OverrideException("No override found for {}".format(current_sign))
        return selected(protocol, **params)

    def override(self, **pattern):
        def decorator(func):
            self.overrides[
                Map(
                    **{
                        k: pattern[k] if k in pattern else self.default_factories[k]()
                        for k in self.pattern.keys()
                    }
                )
            ] = func
            return func

        return decorator
