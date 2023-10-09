from asyncio import PriorityQueue
from typing import Protocol

from integration.utils import Response


class Provider(Protocol):
    def __init__(self, name: str, rate_limit: float):
        self.name = name
        self.rate_limit = rate_limit
        self.last_request_time = 0
        self.enabled = True

    @property
    def is_available(self) -> bool:
        """the logic we must check that we can send a request to this provider"""

    async def send_request(self) -> Response:
        """the logic of sending request with this provider"""
