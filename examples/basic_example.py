import asyncio

from asyncio_hn import ClientHN


async def main(loop):
    # We init the client - extension of aiohttp.ClientSession
    async with ClientHN(loop=loop) as hn:
        # Up to 500 top and top stories (only ids)
        hn_new_stories = await hn.top_stories()
        # Download top 3 story data
        top_posts = await hn.items(hn_new_stories[:2])
        # Download the user data for each story
        users = await hn.users([post.get("by") for post in top_posts])


if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main(loop))
