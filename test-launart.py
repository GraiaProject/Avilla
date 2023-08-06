import asyncio

from avilla.core._vendor.launart import Launart, Service

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
            await asyncio.sleep(3)
            print("unblocking 1")
        async with self.stage("cleanup"):
            print("cleanup")
            await asyncio.sleep(3)


class Test2(Service):
    id = "test2"

    @property
    def required(self) -> set[str]:
        return {"test"}

    @property
    def stages(self) -> set[str]:
        return {"preparing", "blocking", "cleanup"}

    async def launch(self, manager: Launart):
        async with self.stage("preparing"):
            print("prepare2")

        async with self.stage("blocking"):
            print("blocking")
            print("test for sideload")
            manager.add_component(TestSideload())
            await asyncio.sleep(3)
            print("unblocking 2")
            # await asyncio.sleep(1)
            await manager.components["test_sideload"].status.wait_for("blocking")
            print("sideload in blocking, test for active cleanup")
            manager.remove_component("test_sideload")
            await asyncio.sleep(10)

        async with self.stage("cleanup"):
            print("cleanup2")


class TestSideload(Service):
    id = "test_sideload"

    @property
    def required(self) -> set[str]:
        return set()

    @property
    def stages(self) -> set[str]:
        return {"preparing", "blocking", "cleanup"}

    async def launch(self, manager: Launart):
        async with self.stage("preparing"):
            print("prepare in sideload")
            await asyncio.sleep(3)
        async with self.stage("blocking"):
            print("blocking in sideload")
            await asyncio.sleep(3)
            print("unblocking in sideload")
            # print(manager.taskgroup.blocking_task)
        async with self.stage("cleanup"):
            print("cleanup in sideload")
            await asyncio.sleep(3)


art.add_component(TestSrv())
art.add_component(TestService())
art.add_component(Test2())


art.launch_blocking()
