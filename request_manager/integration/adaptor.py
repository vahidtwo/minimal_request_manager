import asyncio
import datetime
import logging
import time

from request_manager.log import logger
from .abc import JobRequestABC, ProviderABC
from .utils import StatusCode, Response


class JobRequest(JobRequestABC):
    def __lt__(self, other: "JobRequest"):
        """Return a string representation of the JobRequest object."""
        return self.priority < other.priority

    def is_ready(self) -> bool:
        """Check if the job request is ready for execution."""
        return time.time() >= self.execution_time


class Provider(ProviderABC):
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

    async def wait_for_rate_limit(self) -> None:
        """
         Wait until the rate limit allows sending a new request.

        Returns:
            bool: True if a request can be sent; otherwise, False.
        """
        while True:
            current_time = time.time()
            if (current_time - self.last_request_time) >= 1 / self.rate_limit:
                return
            else:
                logger.debug(f"\n waiting for rate limit...")
                logger.debug(self)
                # used for not block program in this coroutine
                await asyncio.sleep(0.001)  # TODO find better solution

    async def send_request(self, request: JobRequest) -> Response:
        """
        Send a request using this provider.

        Args:
            request (JobRequest): The request to be sent.

        Returns:
            Response: The response received from the provider.
        """
        logger.debug(f"sending request [{request.name}] with provider {self.name}")
        self.last_request_time = time.time()
        return Response(status_code=StatusCode.SUCCESS, data={"message": "done"})

    def start(self) -> None:
        """
        Enable the provider to start sending requests.
        """
        self.enabled.set()

    async def check_pending_request(self) -> None:
        """
        Check and process pending requests in the queue.
        """
        if self.pending_request_queue.qsize() == 0:
            return
        priority, request = await self.pending_request_queue.get()
        if request.is_ready():
            logger.info(
                f"add pending request[{request.name}] to master queue in provider[{self.name}]"
            )
            await self.queue.put((priority, request))
        else:
            await self.pending_request_queue.put((priority, request))
        self.pending_request_queue.task_done()

    async def _run_job(self) -> None:
        """
        Run jobs in queues according to their priority.
        The enabled provider will send requests based on its rate limit.
        Jobs are collected from the queue.
        If a job is ready (arrived at execution time), send the request.
        If a job is not ready, send it to the pending queue.
        If a job fails, it will be retried up to 3 times before being dropped.
        @todo The hardcoded value for the retry count should be changed and
            the errors should be save for tracking.
        """
        await self.enabled.wait()
        await self.wait_for_rate_limit()
        await self.check_pending_request()
        request: JobRequest
        if self.pending_request_queue.qsize() == 0 and self.queue.qsize() == 0:
            # used for not block program in this coroutine
            await asyncio.sleep(0.001)
        if self.pending_request_queue.qsize() >= 0 and self.queue.qsize() == 0:
            return
        priority, request = await self.queue.get()
        if not request.is_ready():
            logger.info(
                f"add request[{request.name}] to pending queue in provider[{self.name}]"
            )
            self.pending_request_queue.put_nowait((priority, request))
            self.queue.task_done()
            return
        result = await self.send_request(request)
        current_time = datetime.datetime.now().strftime("%H:%M:%S")
        msg = (
            "Sent request {} to provider {} with priority {} at {}"
            " (Execution time: {}) {} request remain"
        ).format(
            request.name,
            request.provider.name,
            request.priority * -1,
            current_time,
            datetime.datetime.fromtimestamp(request.execution_time).strftime(
                "%H:%M:%S"
            ),
            self.get_queue_size(),
        )
        logger.info(f'\n{"+" * 100}')
        logger.info(f"| {msg} |")
        logger.info(f'{"+" * 100}\n')
        if request.retry_count >= 3:
            logging.error(f"{request} in provider {self.name} has been retried 3 times")
            self.queue.task_done()
            return
        if result.status_code != StatusCode.SUCCESS:
            request.retry_count += 1
            await self.queue.put((priority, request))
        self.queue.task_done()

    async def run(self) -> None:
        """
        infinite loop for run jobs on the queue
        if queue is empty it must wait until its filled
        """
        while True:  # TODO replace with better solution
            await self._run_job()

    def stop(self) -> None:
        """
        Disable the provider to stop sending requests.
        """
        self.enabled.clear()

    def get_queue_size(self) -> bool:
        """
        return queues size
        """
        return self.queue.qsize() + self.pending_request_queue.qsize()


class ProviderContainer:
    def __init__(self, provider_list: list[ProviderABC] | None = None):
        self.container = {}
        if provider_list is None:
            return
        for provider in provider_list:
            self.container[provider.name] = provider

    def __getitem__(self, item: ProviderABC | str):
        if isinstance(item, str):
            return self.container[item]
        return self.container[item.name]

    def __setitem__(self, key: str, item: ProviderABC):
        self.container[key] = item

    def __add__(self, other: ProviderABC):
        self.container[other.name] = other
        return self

    def __iter__(self):
        for provider in self.container.values():
            yield provider

    def __len__(self) -> int:
        return len(self.container)
