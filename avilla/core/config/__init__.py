from abc import ABCMeta, abstractmethod
from enum import Enum
from typing import TYPE_CHECKING, Dict, Generic, Hashable, Type, TypeVar, Union
from pydantic import BaseModel

if TYPE_CHECKING:
    from avilla.core import Avilla

EllipsisType = type(...)

TModel = TypeVar("TModel", bound=BaseModel)
TScope = Union[TModel, EllipsisType]
TConfig = Dict["ConfigApplicant", Union[TModel, Dict[TScope, Union[TModel, "ConfigProvider"]]]]

# Applicant, can be a base of a protocol implementation, to make some type hints.
"""
Avilla(
    config={
        OnebotProtocol: {
            entity.account["123456789"]: hocon(OnebotConfig.Ws(...))
        }
    },
    default_config_provider=hocon
)
"""


class InitMoment(Enum):
    before_prepare = "before_prepare"
    before_mainline = "before_mainline"
    after_mainline = "after_mainline"


class ConfigApplicant(Generic[TModel]):
    init_moment: Dict[Type[TModel], InitMoment]

class ConfigProvider(Generic[TModel], metaclass=ABCMeta):
    config_model: Type[TModel]

    def __init__(self, config_model: Type[TModel]) -> None:
        self.config_model = config_model

    @abstractmethod
    async def provide(self, avilla: "Avilla") -> TModel:
        ...


class direct(ConfigProvider[TModel]):
    def __init__(self, config: TModel) -> None:
        self.config_model = type(config)
        self.config = config

    async def provide(self, _) -> TModel:
        return self.config

"""
def _(
    config: Dict[
        ConfigApplicant[TModel], Union[TModel, Dict[TScope, Union[TModel, "ConfigProvider[TModel]"]]]
    ],
    default_config_provider: Type[ConfigProvider],
) -> TConfig:
    return config
"""