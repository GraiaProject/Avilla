from abc import ABCMeta, abstractmethod
from enum import Enum
from pathlib import Path
from typing import (
    TYPE_CHECKING,
    Any,
    Dict,
    Generic,
    Hashable,
    List,
    Optional,
    Type,
    TypeVar,
    Union,
)

from pydantic import BaseModel, Field

if TYPE_CHECKING:
    from avilla.core import Avilla

EllipsisType = type(...)

TModel = TypeVar("TModel", bound=BaseModel)
TScope = Union[TModel, EllipsisType]
TConfig = Dict["ConfigApplicant", Union[TModel, Dict[TScope, Union[TModel, "ConfigProvider"]]]]

# Applicant, can be a base of a protocol implementation, to make some type hints.
# also, Avilla is a applicant.


class ConfigFlushingMoment(Enum):
    before_prepare = "before_prepare"
    before_mainline = "before_mainline"
    in_mainline = "in_mainline"


class ConfigApplicant(Generic[TModel]):
    init_moment: Dict[Type[BaseModel], ConfigFlushingMoment]
    config_model: Type[TModel]


class ConfigProvider(Generic[TModel], metaclass=ABCMeta):
    config: Optional[TModel] = None

    @abstractmethod
    async def provide(
        self, avilla: "Avilla", model: TModel, scope: Any
    ) -> None:  # set self.config, returns None.
        ...

    def get_config(self) -> TModel:
        if self.config is None:
            raise RuntimeError(f"config is not ready.")
        return self.config


class direct(ConfigProvider[TModel]):
    def __init__(self, config: TModel) -> None:
        self.config = config

    async def provide(self, _1, _2, _3):
        pass


class AvillaConfig(BaseModel):
    # Config
    default_local_config_path: Path = Field(default_factory=Path.cwd)
    default_config_provider: Type[ConfigProvider] = direct

    # Builtin Services
    enable_builtin_services: bool = True
    use_memcache: bool = True

    # Builtin Resource Providers
    enable_builtin_resource_providers: bool = True
    use_localfile: bool = True

    # Builtin Utilles
    use_defer: bool = True
