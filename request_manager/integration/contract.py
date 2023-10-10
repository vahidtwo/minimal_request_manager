import asyncio
from asyncio import PriorityQueue

from request_manager.integration.utils import Response

import datetime
import time


class JobRequest:
    def __init__(
        self,
        provider: "Provider",
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


class Provider:
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
        pass

    async def wait_for_rate_limit(self) -> bool:
        """
         Wait until the rate limit allows sending a new request.

        Returns:
            bool: True if a request can be sent; otherwise, False.
        """

    async def send_request(self, request: JobRequest) -> Response:
        """
        Send a request using this provider.

        Args:
            request (JobRequest): The request to be sent.

        Returns:
            Response: The response received from the provider.
        """

    def start(self) -> None:
        """
        Enable the provider to start sending requests.
        """

    async def check_pending_request(self) -> None:
        """
        Check and process pending requests in the queue.
        """

    async def _run_job(self) -> None:
        """run jobs in queues according to their priority
        the enabled provider will send request on its  rate_limit
        """

    async def run(self) -> None:
        """
        infinite loop for run jobs on the queue
        if queue is empty it must wait until its filled
        """
        while True:
            await self._run_job()

    async def stop(self) -> None:
        """
        Disable the provider to stop sending requests.
        """
