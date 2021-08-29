from graia.broadcast.entities.dispatcher import BaseDispatcher
from graia.broadcast.entities.event import Dispatchable


class ServiceOnline(Dispatchable):
    @staticmethod
    def get_ability_id() -> str:
        return "event::ServiceOnline"

    class Dispatcher(BaseDispatcher):
        @staticmethod
        async def catch(interface):
            return


class ServiceOffline(Dispatchable):
    @staticmethod
    def get_ability_id() -> str:
        return "event::ServiceOffline"

    class Dispatcher(BaseDispatcher):
        @staticmethod
        async def catch(interface):
            return


class NetworkConnected(Dispatchable):
    @staticmethod
    def get_ability_id() -> str:
        return "event::NetworkConnected"

    class Dispatcher(BaseDispatcher):
        @staticmethod
        async def catch(interface):
            return
