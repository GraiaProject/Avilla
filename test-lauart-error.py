import asyncio

from avilla.core._vendor.launart import Launart, Service
from avilla.core._vendor.launart.utilles import any_completed

art = Launart()


async def _raise(manager: Launart):
    while not manager.status.exiting:
        await asyncio.sleep(1)
        print(1)
        raise ValueError(1)


class TestSrv(Service):
    id = "test_srv"

    @property
    def required(self) -> set[str]:
        return set()

    @property
    def stages(self) -> set[str]:
        return {"blocking", "cleanup"}

    async def launch(self, manager: Launart):
        async with self.stage("blocking"):
            print("TestSrv: blocking TestInterface")
            await _raise(manager)

        async with self.stage("cleanup"):
            print("TestSrv: cleaned")
            await asyncio.sleep(0.1)


class TestService(Service):
    id = "test"
    srv = TestSrv()

    @property
    def required(self):
        return {"test_srv"}

    @property
    def stages(self) -> set[str]:
        return {"preparing", "blocking", "cleanup"}

    async def launch(self, manager: Launart):
        async with self.stage("preparing"):
            print("prepare")
            await asyncio.sleep(3)
        async with self.stage("blocking"):
            await any_completed(manager.status.wait_for_sigexit(), self.srv.status.wait_for("blocking-completed"))
        async with self.stage("cleanup"):
            print("cleanup")
            await asyncio.sleep(3)


art.add_component(TestSrv())
art.add_component(TestService())

art.launch_blocking()
