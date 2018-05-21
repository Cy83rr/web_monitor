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


async def fetch(session, url, timeout_s, content):
    log = logging.getLogger(__name__)
    try:
        with async_timeout.timeout(timeout_s):
            start_time = time.time()
            async with session.get(url) as response:
                if response.status != 200:
                    raise ConnectionProblem(url, "HTML status code: %s".format(response.status))
                text = await response.text()
            end_time = time.time()
    except ConnectionProblem as ex:
        raise ex
    except (asyncio.TimeoutError, aiohttp.ClientConnectorError) as ex:
        if isinstance(ex, asyncio.TimeoutError):
            msg = type(ex)
        else:
            msg = str(ex)
        raise ConnectionProblem(url, msg)
    content_ok = content in text
    log.info('%s\t%s\t%s', url, content_ok, end_time - start_time)


async def do_request(url, period_ms, timeout_s, content):
    async with aiohttp.ClientSession() as session:
        log = logging.getLogger(__name__)
        while True:
            await asyncio.sleep(period_ms / 1000)
            future = asyncio.ensure_future(fetch(session, url, timeout_s, content))

            def callback(fut):
                ex = fut.exception()
                if isinstance(ex, ConnectionProblem):
                    log.error('%s\tConnection problem\tSpecific error: %s', ex.url, ex.error_msg)
                elif ex:
                    log.critical('%s\tUNKNOWN ERROR', url)

            future.add_done_callback(callback)


def start_app(config):
    log = logging.getLogger(__name__)
    log.setLevel(logging.DEBUG)
    console_h = logging.StreamHandler()
    console_h.setLevel(logging.DEBUG)
    log_path = config['general']['log_path']
    file_h = logging.FileHandler(log_path, 'w')
    file_h.setLevel(config['general']['file_log_level'])
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

    console_h.setFormatter(formatter)
    file_h.setFormatter(formatter)

    log.addHandler(console_h)
    log.addHandler(file_h)

    period_ms = int(config['general']['checking_period'])
    timeout_s = int(config['general']['timeout'])
    web_dict = config['url_content']

    loop = asyncio.get_event_loop()
    futures = []
    for url, content in web_dict.items():
        log.debug('Key: %s', url)
        future = asyncio.ensure_future(do_request(url, period_ms, timeout_s, content))
        futures.append(future)
    loop.run_until_complete(asyncio.gather(*futures, return_exceptions=True))


def main(config):
    processes = []
    server_process = Process(target=server.create_app)
    server_process.start()
    processes.append(server_process)
    requests_process = Process(target=start_app, args=(config,))
    requests_process.start()

    for server_process in processes:
        server_process.join()
