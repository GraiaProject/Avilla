from graia.broadcast.entities.event import Dispatchable
from graia.broadcast.entities.dispatcher import BaseDispatcher

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