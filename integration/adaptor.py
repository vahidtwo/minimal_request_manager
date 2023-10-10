import datetime
import time

from integration.request import Request
from integration.utils import StatusCode, Response
from log import logger


class Provider:
    def __init__(self, name, rate_limit):
        self.name = name
        self.rate_limit = rate_limit
        self.last_request_time = 0
        self.enabled = True

    @property
    def is_available(self) -> bool:
        """the logic we must check that we can send a request to this provider"""
        current_time = time.time()
        if self.enabled and (current_time - self.last_request_time) >= 1 / self.rate_limit:
            self.last_request_time = current_time
            return True
        return False

    async def send_request(self) -> Response:
        """the logic of sending request with this provider"""
        print(f"sending request to provider {self.name}")
        return Response(status_code=StatusCode.SUCCESS, data={})

    def __repr__(self):
        last_request_time_formated = datetime.datetime.fromtimestamp(self.last_request_time).strftime(
            "%Y-%m-%d %H:%M:%S"
        )
        return (
            f"Provider(name={self.name}, rate_limit={self.rate_limit}/s,"
            f" last_request_time={last_request_time_formated}, enabled={self.enabled})"
        )
