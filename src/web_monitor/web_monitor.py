"""
Creates the logger, processes and threads, initializes everything
"""
import asyncio
import logging
import time
from multiprocessing import Process

import aiohttp
import async_timeout

from src.web_monitor.server import server
from src.web_monitor.utils.custom_errors import ConnectionProblem

WAIT_TIMEOUT = 1  # in seconds


async def fetch(session, url, content):
    log = logging.getLogger(__name__)
    try:
        # with async_timeout.timeout(WAIT_TIMEOUT):
        #     start_time = time.time()
        #     async with session.get(url) as response:
        #         text = await response.text()
        #     end_time = time.time()
        start_time = time.time()
        async with session.get(url) as response:
            text = await response.text()
        end_time = time.time()
    except Exception as e:
        raise ConnectionProblem(url, e)
    log.info('%s\t%s\t%s', url, content in text, end_time - start_time)


async def do_request(url, period_ms, content):
    async with aiohttp.ClientSession() as session:
        log = logging.getLogger(__name__)
        while True:
            await asyncio.sleep(period_ms / 1000)
            future = asyncio.ensure_future(fetch(session, url, content))

            def callback(fut):
                ex = fut.exception()
                if type(ex) is ConnectionProblem:
                    log.error('%s\tConnection problem\tSpecific error type: %s', ex.url, type(ex.error_msg))
                elif ex:
                    log.critical('UNKNOWN ERROR')

            future.add_done_callback(callback)


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
    futures = []
    for url, content in web_dict.items():
        log.debug('Key: %s', url)
        future = asyncio.ensure_future(do_request(url, period_ms, content))
        futures.append(future)
    loop.run_until_complete(asyncio.gather(*futures, return_exceptions=True))


def main(config):
    processes = []
    p = Process(target=server.create_app)
    p.start()
    processes.append(p)
    p2 = Process(target=start_app, args=(config,))
    p2.start()

    for p in processes:
        p.join()
