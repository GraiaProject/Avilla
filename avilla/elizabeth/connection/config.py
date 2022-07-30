from __future__ import annotations

from dataclasses import dataclass, field
from typing import TypeVar, Union

from yarl import URL


@dataclass
class HttpClientConfig:
    account: str
    verify_key: str
    host: str = "http://localhost:8080"

    def get_url(self, route: str) -> str:
        return str((URL(self.host) / route))

    @classmethod
    def cast(cls, config: U_Config) -> HttpClientConfig:
        if isinstance(config, HttpClientConfig):
            return config
        elif isinstance(config, WebsocketClientConfig):
            return HttpClientConfig(
                config.account,
                config.http_verify_key or config.verify_key,
                config.http_host or config.host,
            )
        elif isinstance(config, HttpServerConfig):
            return HttpClientConfig(
                config.account,
                config.http_verify_key or "",
                config.http_host or "http://localhost:8080",
            )
        elif isinstance(config, WebsocketServerConfig):
            return HttpClientConfig(
                config.account,
                config.http_verify_key or config.verify_key,
                config.http_host or "http://localhost:8080",
            )
        raise TypeError(f"{config} is not instance of {U_Config}")

    @property
    def use_http(self):
        return False


@dataclass
class WebsocketClientConfig:
    account: str
    verify_key: str
    host: str = "http://localhost:8080"
    http_verify_key: str | None = None
    http_host: str | None = None
    use_http: bool = False

    def get_url(self, route: str) -> str:
        return str((URL(self.host) / route))


@dataclass
class WebsocketServerConfig:
    account: str
    verify_key: str
    path: str = "/"
    params: dict[str, str] = field(default_factory=dict)
    headers: dict[str, str] = field(default_factory=dict)
    http_verify_key: str | None = None
    http_host: str | None = None
    use_http: bool = False


@dataclass
class HttpServerConfig:
    account: str
    path: str = "/"
    headers: dict[str, str] = field(default_factory=dict)
    http_verify_key: str | None = None
    http_host: str | None = None

    @property
    def use_http(self):
        return True


U_Config = Union[HttpClientConfig, WebsocketClientConfig, WebsocketServerConfig, HttpServerConfig]

T_Config = TypeVar("T_Config", bound=U_Config)
