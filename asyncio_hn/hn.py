#!/usr/bin/env python3.6
import asyncio
import logging

import aiohttp
import tqdm
from aiohttp import HttpProcessingError

URL_GET_POST = "https://hacker-news.firebaseio.com/v0/item/{}.json"
URL_GET_USER = "https://hacker-news.firebaseio.com/v0/user/{}.json"
URL_MAX_ITEM = 'https://hacker-news.firebaseio.com/v0/maxitem.json'
URL_TOP_STORIES = "https://hacker-news.firebaseio.com/v0/topstories.json"
URL_NEW_STORIES = "https://hacker-news.firebaseio.com/v0/newstories.json"
URL_BEST_STORIES = "https://hacker-news.firebaseio.com/v0/beststories.json"
URL_UPDATES = "https://hacker-news.firebaseio.com/v0/updates.json"
URL_ASK_STORIES = "https://hacker-news.firebaseio.com/v0/askstories.json"
URL_SHOW_STORIES = "https://hacker-news.firebaseio.com/v0/showstories.json"
URL_JOB_STORIES = "https://hacker-news.firebaseio.com/v0/jobstories.json"
# The max tcp connection we open
MAX_CONNECTION = 1000

# setting up logger
logger = logging.getLogger(__name__)
console = logging.StreamHandler()
logger.addHandler(console)


class ClientHN(aiohttp.ClientSession):
    def __init__(self, queue_size=10, progress_bar=False, debug=False, num_dlq_consumers=10, **kwargs):
        super(ClientHN, self).__init__(**kwargs)
        self.queue_size = queue_size
        self.connector_limit = self.connector.limit
        self._responses = []
        self.progress_bar = progress_bar
        self.num_dlq_consumers = num_dlq_consumers
        if debug:
            logger.setLevel(logging.DEBUG)

    async def single_download(self, url):
        async with self.get(url) as resp:
            return await resp.json()

    async def multi_download(self, itr, url, num_of_consumers=None, desc=""):
        queue, dlq, responses = asyncio.Queue(
            maxsize=self.queue_size), asyncio.Queue(), []
        num_of_consumers = num_of_consumers or min(self.connector_limit, self.try_get_itr_len(itr))
        consumers = [asyncio.ensure_future(
            self._consumer(main_queue=queue, dlq=dlq, responses=responses)) for _ in
                     range(num_of_consumers or self.connector_limit)]
        dlq_consumers = [asyncio.ensure_future(
            self._consumer(dlq, dlq, responses)) for _ in range(self.num_dlq_consumers)]
        produce = await self._produce(itr, url, queue, desc=desc)
        await queue.join()
        await dlq.join()
        for consumer in consumers + dlq_consumers:
            consumer.cancel()
        return responses

    def try_get_itr_len(self, itr):
        try:
            return len(itr)
        except TypeError:
            return 1000000

    async def _produce(self, items, base_url, queue, desc=""):
        for item in tqdm.tqdm(items, desc=desc + " (Estimation)", disable=not self.progress_bar):
            await queue.put(base_url.format(item))

    async def _consumer(self, main_queue, dlq, responses):
        while True:
            try:
                url = await main_queue.get()
                async with self.get(url, timeout=10) as response:
                    resp = response
                    resp.raise_for_status()
                    responses.append(await resp.json())
                    # Notify the queue that the item has been processed
                    main_queue.task_done()

            except (HttpProcessingError, asyncio.TimeoutError) as e:
                logger.debug("Problem with %s, Moving to DLQ" % url)
                await dlq.put(url)
                main_queue.task_done()

    async def top_stories(self):
        return await self.single_download(URL_TOP_STORIES)

    async def best_stories(self):
        return await self.single_download(URL_BEST_STORIES)

    async def new_stories(self):
        return await self.single_download(URL_NEW_STORIES)

    async def ask_stories(self):
        return await self.single_download(URL_ASK_STORIES)

    async def updates(self):
        return await self.single_download(URL_UPDATES)

    async def job_stories(self):
        return await self.single_download(URL_JOB_STORIES)

    async def max_item(self):
        return await self.single_download(URL_MAX_ITEM)

    async def users(self, itr_users, num_of_futures=None):
        return await self.multi_download(itr_users, URL_GET_USER, num_of_futures, "Download users")

    async def items(self, posts_itr, num_of_futures=None):
        return await self.multi_download(posts_itr, URL_GET_POST, num_of_futures, "Download items")

    async def last_n_items(self, n, num_of_futures=None):
        max_item = await self.max_item()
        return await self.multi_download(range(max_item, max_item - n, -1), URL_GET_POST, num_of_futures,
                                         "Download last N posts")
