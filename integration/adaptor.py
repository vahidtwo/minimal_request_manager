import asyncio
import datetime
import logging
import time
from asyncio import PriorityQueue

from integration.request import Request
from integration.utils import StatusCode, Response
from log import logger


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

    def __init__(self, name, rate_limit):
        self.name = name
        self.rate_limit = rate_limit
        self.last_request_time = 0
        self.enabled = asyncio.Event()
        self.enabled.set()
        self.queue = PriorityQueue()
        self.pending_request_queue = PriorityQueue()

    async def wait_for_rate_limit(self) -> bool:
        """
         Wait until the rate limit allows sending a new request.

        Returns:
            bool: True if a request can be sent; otherwise, False.
        """
        while True:
            current_time = time.time()

            if (current_time - self.last_request_time) >= 1 / self.rate_limit:
                self.last_request_time = current_time
                return True
            else:
                logger.debug(f"waiting for rate limit...")
                logger.debug(self)

    async def send_request(self, request: Request) -> Response:
        """
        Send a request using this provider.

        Args:
            request (Request): The request to be sent.

        Returns:
            Response: The response received from the provider.
        """
        logger.debug(f"sending request [{request.name}] with provider {self.name}")
        return Response(status_code=StatusCode.SUCCESS, data={"message": "done"})

    def start(self):
        """
        Enable the provider to start sending requests.
        """
        self.enabled.set()

    async def check_pending_request(self):
        """
        Check and process pending requests in the queue.
        """
        if self.pending_request_queue.qsize() > 0:
            priority, request = await self.pending_request_queue.get()
            if request.is_ready:
                logger.info(
                    f"add pending request[{request.name}] to master queue in provider[{self.name}]"
                )
                await self.queue.put((priority, request))
            else:
                await self.pending_request_queue.put((priority, request))
            self.pending_request_queue.task_done()

    async def run(self):
        """
        Start the provider to send requests.
        """
        while True:
            await self.enabled.wait()
            await self.wait_for_rate_limit()
            await self.check_pending_request()
            request: Request
            priority, request = await self.queue.get()
            if request.is_ready is False:
                logger.info(
                    f"add request[{request.name}] to pending queue in provider[{self.name}]"
                )
                self.pending_request_queue.put_nowait((priority, request))
                self.queue.task_done()
                continue
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
                self.queue.qsize(),
            )
            logger.info("{}\n| {} |\n{}".format("+" * 100, msg, "+" * 100))
            if result.status_code != StatusCode.SUCCESS:
                if request.retry_count >= 3:
                    logging.error(
                        f"{request} in provider {self.name} has been retried 3 times"
                    )
                    self.queue.task_done()
                    continue
                request.retry_count += 1
                await self.queue.put((priority, request))
            self.queue.task_done()

    async def stop(self):
        """
        Disable the provider to stop sending requests.
        """
        self.enabled.clear()

    def __repr__(self):
        last_request_time_formated = datetime.datetime.fromtimestamp(
            self.last_request_time
        ).strftime("%Y-%m-%d %H:%M:%S")
        return (
            f"Provider(name={self.name}, rate_limit={self.rate_limit}/s,"
            f" last_request_time={last_request_time_formated}, enabled={self.enabled.is_set()})"
        )
