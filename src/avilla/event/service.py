from graia.broadcast.entities.dispatcher import BaseDispatcher
from graia.broadcast.entities.event import Dispatchable


class ServiceOnline(Dispatchable):
    class Dispatcher(BaseDispatcher):
        @staticmethod
        async def catch(interface):
            return


class ServiceOffline(Dispatchable):
    class Dispatcher(BaseDispatcher):
        @staticmethod
        async def catch(interface):
            return


class NetworkConnected(Dispatchable):
    class Dispatcher(BaseDispatcher):
        @staticmethod
        async def catch(interface):
            return
