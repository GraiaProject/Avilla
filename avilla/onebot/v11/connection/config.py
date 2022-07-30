from yarl import URL


class OneBot11Config:
    access_token: str
    host: URL

    def __init__(self, access_token: str = "", host: URL | str = URL("http://localhost:8080")) -> None:
        self.access_token = access_token
        self.host = URL(host)


class OneBot11HttpClientConfig(OneBot11Config):
    pass


class OneBot11HttpServerConfig(OneBot11Config):
    pass


class OneBot11WebsocketClientConfig(OneBot11Config):
    pass


class OneBot11WebsocketServerConfig(OneBot11Config):
    pass


OneBot11Config(access_token="", host="http://localhost:8080")
