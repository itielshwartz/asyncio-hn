import asyncio
import json

import aiohttp
from asyncio_hn.hn_old import ClientHN

N = 1_000_000


async def advance_run(loop):
    # We init the client - extension of aiohttp.ClientSession
    conn = aiohttp.TCPConnector(limit=1000, loop=loop)
    async with ClientHN(loop=loop, queue_size=1000, connector=conn, progress_bar=True, debug=True) as hn:
        # Download the last 1,000,000 stories
        hn_new_stories = await hn.last_n_items(n=N)
        with open("1_million_posts.json", "w") as f:
            json.dump(hn_new_stories, f)


if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.run_until_complete(advance_run(loop))
