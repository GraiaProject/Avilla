import asyncio

from yarl import URL
from avilla.core.network.aiohttp.schema import HttpRequestSchema

from avilla.core.network.aiohttp.service import AiohttpHttpClient
from avilla.core.network.builtins.partitions import Read
from avilla.core.transformers import u8_encode, u8_string, json_encode, json_decode 
from avilla.core.stream import Stream

loop = asyncio.get_event_loop()
net = AiohttpHttpClient()


async def i():
    async with net.postconnect(
        HttpRequestSchema(
            URL("http://httpbin.org/anything"),
            "POST",
            data=await Stream({}).transform(json_encode()).transform(u8_encode).unwrap(),
        )
    ) as resp:
        print(
            await Stream(await resp.partition(Read()))
            .transform(u8_string)
            .transform(json_decode())
            .unwrap()
        )


loop.run_until_complete(i())
