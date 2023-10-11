import asyncio
from abc import ABC, abstractmethod
from asyncio import PriorityQueue
from typing import Protocol

from request_manager.integration.utils import Response

import datetime
import time


class JobRequestABC(ABC):
    def __init__(
        self,
        provider: "ProviderABC",
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
        self.name = name
        self.provider = provider
        self.retry_count = 0
        # for use in PriorityQueue we must invert the priority to act as a max-heap
        self.priority = priority * -1
        if isinstance(execution_after, datetime.datetime):
            self.execution_time = execution_after.timestamp()
        elif isinstance(execution_after, int):
            self.execution_time = time.time() + execution_after

    def __repr__(self):
        return (
            f"JobRequest(name={self.name}, priority={self.priority * -1},"
            f" execution_time={datetime.datetime.fromtimestamp(self.execution_time).strftime('%H:%M:%S')},"
            f" provider={self.provider.name})"
        )

    @abstractmethod
    def __lt__(self, other: "JobRequestABC"):
        """Return a string representation of the JobRequest object."""

    @abstractmethod
    def is_ready(self) -> bool:
        """Check if the job request is ready for execution."""


class ProviderABC(ABC):
    """
    Represents a service provider for sending requests.

    Attributes:
        name (str): The name of the provider.
        rate_limit (float): The rate limit for sending requests per second.
        last_request_time (float): The timestamp of the last sent request.
        enabled (asyncio.Event): An event that controls whether the provider is enabled.
        queue (asyncio.PriorityQueue): A priority queue for pending requests.
        pending_request_queue (asyncio.PriorityQueue): A priority queue for pending requests that are not ready.
    """

    def __init__(self, name: str, rate_limit: float) -> None:
        self.name = name
        self.rate_limit = rate_limit
        self.last_request_time = time.time() - (1 / rate_limit)
        self.enabled = asyncio.Event()
        self.enabled.set()
        self.queue = PriorityQueue()
        self.pending_request_queue = PriorityQueue()

    @abstractmethod
    async def wait_for_rate_limit(self) -> bool:
        """
         Wait until the rate limit allows sending a new request.

        Returns:
            bool: True if a request can be sent; otherwise, False.
        """

    @abstractmethod
    async def send_request(self, request: JobRequestABC) -> Response:
        """
        Send a request using this provider.

        Args:
            request (JobRequest): The request to be sent.

        Returns:
            Response: The response received from the provider.
        """

    @abstractmethod
    def start(self) -> None:
        """
        Enable the provider to start sending requests.
        """

    @abstractmethod
    async def check_pending_request(self) -> None:
        """
        Check and process pending requests in the queue.
        """

    @abstractmethod
    async def _run_job(self) -> None:
        """run jobs in queues according to their priority
        the enabled provider will send request on its  rate_limit
        """

    @abstractmethod
    async def run(self) -> None:
        """
        infinite loop for run jobs on the queue
        if queue is empty it must wait until its filled
        """

    @abstractmethod
    async def stop(self) -> None:
        """
        Disable the provider to stop sending requests.
        """

    def __repr__(self):
        last_request_time_formated = datetime.datetime.fromtimestamp(
            self.last_request_time
        ).strftime("%Y-%m-%d %H:%M:%S")
        return (
            f"Provider(name={self.name}, rate_limit={self.rate_limit}/s,"
            f" last_request_time={last_request_time_formated}, enabled={self.enabled.is_set()})"
        )

    @abstractmethod
    def get_queue_size(self) -> bool:
        """
        return queue size
        """
