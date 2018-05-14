"""
Creates the logger, processes and threads, initializes everything
"""
import asyncio
import time
from contextlib import suppress
from multiprocessing import Process
from threading import Thread

import aiohttp

#from src.web_monitor.server.server import WebMonitorServer
# TODO: do this for unlimited time, then scale to a list of urls
from src.web_monitor.server import server


async def do_request(url, period_ms, content):
    p = Periodic(url, period_ms, content)
    try:
        print('Start')
        await p.start()
        await asyncio.sleep(3.1) # it repeats the task as many times it can in the sleep

        print('Stop')
        await p.stop()
        await asyncio.sleep(3.1)

        print('Start')
        await p.start()
        await asyncio.sleep(3.1)
    finally:
        await p.stop()  # we should stop task finally


    # start_time = time.time()
    # response = await aiohttp.request('GET', url)
    # end_time = time.time()
    # print(response)
    # #result = check_response(response)
    #
    # return end_time - start_time

class Periodic:
    def __init__(self, url, time, content):
        self.url = url
        self.time = time
        self.is_started = False
        self.content = content
        self._task = None

    async def start(self):
        if not self.is_started:
            self.is_started = True
            # Start task to call func periodically:
            self._task = asyncio.ensure_future(self._run())

    async def stop(self):
        if self.is_started:
            self.is_started = False
            # Stop task and await it stopped:
            self._task.cancel()
            with suppress(asyncio.CancelledError):
                await self._task

    async def _run(self):
        async with aiohttp.ClientSession() as session:
            while True:
                await asyncio.sleep(self.time/1000)
                start_time = time.time()
                response = await fetch(session, self.url)
                end_time = time.time()
                print(self.url)
                print('Content OK?', self.content in response)
                print(end_time - start_time)

async def fetch(session, url):
    async with session.get(url) as response:
        return await response.text()

def start_app(config):
    # server = WebMonitorServer()
    # server.run_server()

    period_ms = 100
    web_dict = config['url_content']


    #task = asyncio.Task(do_request(url))
    loop = asyncio.get_event_loop()
    for url, content in web_dict.items():
        print('Key: ', url)
        #loop.run_until_complete(do_request(url, period_ms, web_dict[url]))
        loop.create_task(do_request(url, period_ms, web_dict[url]))
    loop.run_forever()

    #loop.create_task(do_request(url))
    #loop.call_later(period_ms, lambda: asyncio.Task.cancel) # not sure this works correctly - might be better to create tasks explicitly
    # loop.call_later(period_ms, task.cancel)
    # try:
    #     loop.run_until_complete(task)
    # except asyncio.CancelledError:
    #     pass
def main(config):

    processes = []
    p = Process(target=server.create_app)
    p.start()
    processes.append(p)
    p2 = Process(target=start_app, args=(config,))
    p2.start()

    for p in processes:
        p.join()