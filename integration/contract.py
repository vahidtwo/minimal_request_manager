import asyncio
from asyncio import PriorityQueue
from typing import Protocol

from integration.adaptor import Request
from integration.utils import Response


class Provider(Protocol):
    def __init__(self, name, rate_limit):
        self.name = name
        self.rate_limit = rate_limit
        self.last_request_time = 0
        self.enabled = asyncio.Event()
        self.enabled.set()
        self.queue = PriorityQueue()

    async def wait_for_rate_limit(self) -> bool:
        """the logic we must check that we can send a request to this provider"""

    async def send_request(self, request: Request) -> Response:
        """the logic of sending request with this provider"""

    def start(self):
        pass

    async def check_pending_request(self):
        pass

    async def run(self):
        """start the provider to send requests"""

    async def stop(self):
        pass
