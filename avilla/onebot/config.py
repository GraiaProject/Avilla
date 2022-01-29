import json
from typing import Callable, Optional

from pydantic import BaseModel
from yarl import URL

from avilla.core.config import ConfigApplicant, ConfigFlushingMoment, TModel


class OnebotConnectionConfig(BaseModel):
    access_token: Optional[str] = None

    data_parser: Callable[[str], object] = json.loads
    data_serializer: Callable[[object], str] = json.dumps


class OnebotHttpClientConfig(OnebotConnectionConfig):
    url: URL


class OnebotWsClientConfig(OnebotConnectionConfig):
    url: URL


class OnebotHttpServerConfig(BaseModel):
    api_root: str = "/onebot"


class OnebotWsServerConfig(BaseModel):
    api_root: str = "/onebot"
