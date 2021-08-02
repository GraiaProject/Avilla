from typing import Dict, Union

from pydantic import BaseSettings, BaseModel
from yarl import URL

from avilla.network.signatures import ClientCommunicationMethod, ServiceCommunicationMethod


class HttpCommunication(BaseModel, ClientCommunicationMethod):
    api_root: URL

    class Config:
        arbitrary_types_allowed = True


class ReverseHttpCommunication(BaseModel, ServiceCommunicationMethod):
    listening_host: str = "0.0.0.0"
    listening_port: int

    secret: str = None
    timeout: int = -1


class WebsocketCommunication(BaseModel, ClientCommunicationMethod):
    api_root: URL

    class Config:
        arbitrary_types_allowed = True


class ReverseWebsocketCommunication(BaseModel, ServiceCommunicationMethod):
    listening_host: str = "0.0.0.0"
    listening_port: int


class OnebotConfig(BaseSettings):
    access_token: str = None
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
