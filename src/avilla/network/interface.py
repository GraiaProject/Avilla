from typing import Dict, Type, TypeVar, Union

from avilla.network.client import Client
from avilla.network.service import Service

T = TypeVar("T")


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

    def get_network(self, network_id: str):
        if network_id not in self.networks:
            raise TypeError("network not registered")
        return self.networks[network_id]

    def get_by_class(self, network_class: Type[T]) -> T:
        for network in self.networks.values():
            if isinstance(network, network_class):  # type: ignore
                return network
        else:
            raise TypeError("no such network")
