import asyncio
import datetime
from asyncio import Task

from integration.adaptor import Provider, Request
from log import logger


class Controller:
    tasks: list[Task]
    providers = dict[str, Provider]

    def __init__(self, providers: list[Provider]):
        self.providers = {provider.name: provider for provider in providers}
        self.tasks = []

    @staticmethod
    def new_request_received(
        provider: Provider,
        priority: int,
        execution_after: datetime.datetime | int = 0,
        request_name: str = "",
    ) -> Request:
        request = Request(
            name=request_name,
            provider=provider,
            priority=priority,
            execution_after=execution_after,
        )
        provider.queue.put_nowait((request.priority, request))
        logger.info(f"added {request}")
        return request

    def start(self):
        self.tasks = [
            asyncio.create_task(provider.run()) for provider in self.providers.values()
        ]

    async def wait_for_complete(self):
        for provider in self.providers.values():
            if provider.enabled.is_set():
                await provider.queue.join()
                await provider.pending_request_queue.join()

    def stop(self):
        for task in self.tasks:
            task.cancel()
