import asyncio
import datetime
from asyncio import PriorityQueue
from typing import Protocol

from request_manager.integration.adaptor import JobRequest
from request_manager.integration.utils import Response


class JobRequestProtocol(Protocol):
    provider: "ProviderProtocol"
    priority: int
    execution_after: datetime.datetime | int = 0
    name: str = ""

    def __init__(
        self,
        provider: "ProviderProtocol",
        priority: int,
        execution_after: datetime.datetime | int = 0,
        name: str = "",
    ):
        """
        Initialize a JobRequest object.

        Args:
            provider (Provider): The provider associated with this job request.
            priority (int): The priority of the job request. Higher values indicate higher priority.
            execution_after (datetime.datetime | int, optional): The time when the job should be executed.
                It can be either a datetime object or an integer representing seconds from the current time.
                Defaults to 0, which means immediate execution.
            name (str, optional): A name or identifier for the job request. Defaults to an empty string.
        """

    def __lt__(self, other: "JobRequest"):
        """Return a string representation of the JobRequest object."""

    @property
    def is_ready(self) -> bool:
        """Check if the job request is ready for execution."""


class ProviderProtocol(Protocol):
    def __init__(self, name, rate_limit):
        self.name = name
        self.rate_limit = rate_limit
        self.last_request_time = 0
        self.enabled = asyncio.Event()
        self.enabled.set()
        self.queue = PriorityQueue()

    async def wait_for_rate_limit(self) -> bool:
        """the logic we must check that we can send a request to this provider"""

    async def send_request(self, request: JobRequest) -> Response:
        """the logic of sending request with this provider"""

    def start(self):
        pass

    async def check_pending_request(self):
        pass

    async def run(self):
        """start the provider to send requests"""

    async def stop(self):
        pass
