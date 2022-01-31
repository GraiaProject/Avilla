import json
from typing import Callable, Optional

from pydantic import BaseModel
from yarl import URL

from avilla.core.config import ConfigApplicant, ConfigFlushingMoment, TModel


class OnebotConnectionConfig(BaseModel):
    access_token: Optional[str] = None

    resp_timeout: float = 10
    data_parser: Callable[[str], dict] = json.loads
    data_serializer: Callable[[object], str] = json.dumps

    class Config:
        arbitrary_types_allowed = True


class OnebotHttpClientConfig(OnebotConnectionConfig):
    url: URL


class OnebotWsClientConfig(OnebotConnectionConfig):
    url: URL


class OnebotHttpServerConfig(OnebotConnectionConfig):
    api_root: str = "/onebot"


class OnebotWsServerConfig(OnebotConnectionConfig):
    api_root: str = "/onebot"
    universal: str = "/universal"
    api: str = "/api"
    event: str = "/event"
