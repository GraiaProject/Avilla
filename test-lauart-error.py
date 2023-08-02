import asyncio

from launart import Launart, Service

art = Launart()



class TestSrv(Service):
    id = "test_srv"

    @property
    def required(self) -> set[str]:
        return set()

    @property
    def stages(self) -> set[str]:
        return {"preparing"}

    async def launch(self, manager: Launart):
        async with self.stage("preparing"):
            print("TestSrv: prepared TestInterface")

async def _raise():
    await asyncio.sleep(0.1)
    print(1)
    raise RuntimeError(1)


class TestService(Service):
    id = "test"

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
            print("blocking")
            await _raise()
            await asyncio.sleep(3)
            print("unblocking 1")
        async with self.stage("cleanup"):
            print("cleanup")
            await asyncio.sleep(3)



art.add_component(TestSrv())
art.add_component(TestService())

art.launch_blocking()
