import datetime
import time

from integration.utils import StatusCode, Response
from log import logger


class Request:
    def __init__(
        self,
        provider: "Provider",
        priority: int,
        execution_after: datetime.datetime | int = 0,
        name: str = "",
    ):
        self.name = name
        self.provider = provider
        # for use in min-heap we must invert the priority to act as a max-heap
        self.priority = priority * -1
        if execution_after is not None:
            if isinstance(execution_after, datetime.datetime):
                self.execution_time = execution_after.timestamp()
            elif isinstance(execution_after, int):
                self.execution_time = time.time() + execution_after

    def __repr__(self):
        return (
            f"Request(name={self.name}, priority={self.priority * -1},"
            f" execution_time={self.execution_time}, provider={self.provider.name})"
        )

    def __lt__(self, other: "Request"):
        return self.priority < other.priority

    @property
    def is_ready(self) -> bool:
        return time.time() >= self.execution_time


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
