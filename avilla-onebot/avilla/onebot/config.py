from typing import Dict, Optional, Union

from avilla.core.network.signatures import (ClientCommunicationMethod,
                                            ServiceCommunicationMethod)
from pydantic import BaseModel, BaseSettings
from yarl import URL


class HttpCommunication(BaseModel, ClientCommunicationMethod):
    api_root: URL

    class Config:
        arbitrary_types_allowed = True


class ReverseHttpCommunication(BaseModel, ServiceCommunicationMethod):
    listening_host: str = "0.0.0.0"
    listening_port: int

    secret: Optional[str] = None
    timeout: int = -1


class WebsocketCommunication(BaseModel, ClientCommunicationMethod):
    api_root: URL

    class Config:
        arbitrary_types_allowed = True


class ReverseWebsocketCommunication(BaseModel, ServiceCommunicationMethod):
    listening_host: str = "0.0.0.0"
    listening_port: int


class OnebotConfig(BaseSettings):
    access_token: Optional[str] = None
    bot_id: str

    # 暂时只支持 aiohttp 的 client 模式(使用 websocket 获取事件什么的..)
    communications: Dict[
        str,
        Union[
            HttpCommunication,
            ReverseHttpCommunication,
            WebsocketCommunication,
            ReverseWebsocketCommunication,
        ],
    ]
