"""
Creates the logger, processes and threads, initializes everything
"""
import asyncio
import logging
import time
from multiprocessing import Process

import aiohttp

from src.web_monitor.server import server


async def do_request(url, period_ms, content):
    #asyncio.ensure_future
    async with aiohttp.ClientSession() as session:
        log = logging.getLogger(__name__)
        while True:
            await asyncio.sleep(period_ms / 1000)
            start_time = time.time()
            response = await session.get(url)
            text = await response.text()
            end_time = time.time()
            log.info('%s\t%s\t%s', url, content in text, end_time - start_time)


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
