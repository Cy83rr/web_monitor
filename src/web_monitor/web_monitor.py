"""
Creates the logger, processes and threads, initializes everything
"""
import asyncio
import logging
import time
from contextlib import suppress
from multiprocessing import Process

import aiohttp

from src.web_monitor.server import server


async def do_request(url, period_ms, content):
    log = logging.getLogger(__name__)
    p = Periodic(url, period_ms, content)
    try:
        log.debug('Start')
        await p.start()
        await asyncio.sleep(3.1)  # it repeats the task as many times it can in the sleep

        log.debug('Stop')
        await p.stop()
        await asyncio.sleep(3.1)

        log.debug('Start')
        await p.start()
        await asyncio.sleep(3.1)
    finally:
        await p.stop()  # we should stop task finally


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
            log = logging.getLogger(__name__)
            while True:
                await asyncio.sleep(self.time / 1000)
                start_time = time.time()
                response = await fetch(session, self.url)
                end_time = time.time()
                log.info('%s\t%s\t%s', self.url, self.content in response, end_time - start_time)


async def fetch(session, url):
    async with session.get(url) as response:
        return await response.text()


def start_app(config):
    log = logging.getLogger(__name__)
    log.setLevel(logging.DEBUG)
    ch = logging.StreamHandler()
    ch.setLevel(logging.DEBUG)
    log_path = config['general']['log_path']
    fh = logging.FileHandler(log_path, 'w')
    fh.setLevel(config['general']['file_log_level'])
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

    ch.setFormatter(formatter)
    fh.setFormatter(formatter)

    log.addHandler(ch)
    log.addHandler(fh)
    period_ms = int(config['general']['checking_period'])
    web_dict = config['url_content']

    loop = asyncio.get_event_loop()
    for url, content in web_dict.items():
        log.debug('Key: %s', url)
        loop.create_task(do_request(url, period_ms, web_dict[url]))
    loop.run_forever()


def main(config):
    processes = []
    p = Process(target=server.create_app)
    p.start()
    processes.append(p)
    p2 = Process(target=start_app, args=(config,))
    p2.start()

    for p in processes:
        p.join()
