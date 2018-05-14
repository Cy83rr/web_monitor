import logging

import requests
from requests import HTTPError, Timeout

from src.web_monitor.verifiers.content_checker import ContentChecker

TIMEOUT_MS = 1000


class Connector:
    """
    Makes periodic HTTP requests for a web page, measures the time
    """

    def __init__(self, http_address, period_ms):
        self.url = http_address
        self.period_ms = period_ms
        self.content_checker = ContentChecker(http_address)

    def _request(self):
        log = logging.getLogger(__name__)
        try:
            response = requests.get(self.url, timeout=TIMEOUT_MS)
        except ConnectionError as e:
            log.error("[%s] Connection problem! Exact error: %s", self.url, str(e))
            return None
        except HTTPError:
            log.error("[%s] Unsuccessful request! Exact status code: %s", self.url, response.status_code)
            return None
        except Timeout:
            log.error("[%s] Connection problem! Timeout (%s)", self.url, TIMEOUT_MS)
            return None

    def check_content(self, response):
        pass

    def check_periodically(self):
        # for a period of ms, make a request
        pass
