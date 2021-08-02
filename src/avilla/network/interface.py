from typing import Dict, Union

from avilla.network.client import Client
from avilla.network.service import Service


class NetworkInterface:
    networks: Dict[str, Union[Client, Service]]

    def __init__(self, networks: Dict[str, Union[Client, Service]]):
        self.networks = networks

    def register_network(self, network_id: str, network: Union[Client, Service]) -> None:
        if network_id in self.networks:
            raise TypeError("network already registered")
        self.networks[network_id] = network

    def unregister_network(self, network_id: str) -> None:
        if network_id not in self.networks:
            raise TypeError("network not registered")
        del self.networks[network_id]

    def get_network(self, network_id: str) -> Union[Client, Service]:
        if network_id not in self.networks:
            raise TypeError("network not registered")
        return self.networks[network_id]
