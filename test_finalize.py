from weakref import finalize
import asyncio

def r(c):
    print(c)

async def x(q):
    await asyncio.sleep(1)
    print(q)

class s:
    def __init__(self):
        finalize(self, asyncio.get_running_loop().create_task, x("24124"))

async def z():
    s()

loop = asyncio.get_event_loop()
loop.run_until_complete(z())
loop.run_until_complete(asyncio.sleep(1))