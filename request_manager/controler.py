import asyncio
import datetime
from asyncio import Task

from integration.contract import ProviderProtocol, JobRequestProtocol
from log import logger


class Controller:
    tasks: list[Task]
    providers = dict[str, ProviderProtocol]

    def __init__(self, providers: list[ProviderProtocol] | None = None):
        """
        Initialize a Controller object.

        Args:
            providers (list[ProviderProtocol]): A list of ProviderProtocol objects to manage.
        """
        self.providers = (
            {provider.name: provider for provider in providers}
            if providers is not None
            else dict()
        )
        self.tasks = []

    def add_provider(self, provider: ProviderProtocol):
        self.providers[provider.name] = provider

    @staticmethod
    def new_request_received(
        provider: ProviderProtocol,
        priority: int,
        execution_after: datetime.datetime | int = 0,
        request_name: str = "",
    ) -> JobRequestProtocol:
        """
         Create a new job request and add it to the provider's queue.

        Args:
            provider (ProviderProtocol): The provider to which the job request is associated.
            priority (int): The priority of the job request.
            execution_after (datetime.datetime | int, optional): The time when the job should be executed.
                It can be either a datetime object or an integer representing seconds from the current time.
                Defaults to 0, which means immediate execution.
            request_name (str, optional): A name or identifier for the job request. Defaults to an empty string.

        Returns:
            JobRequestProtocol: The created JobRequestProtocol object.
        """
        request = JobRequestProtocol(
            name=request_name,
            provider=provider,
            priority=priority,
            execution_after=execution_after,
        )
        provider.queue.put_nowait((request.priority, request))
        logger.info(f"added {request}")
        return request

    def start(self):
        """
        Start the providers' tasks.
        This method creates tasks for each provider to run concurrently
        """
        self.tasks = [
            asyncio.create_task(provider.run()) for provider in self.providers.values()
        ]

    async def wait_for_complete(self):
        """
        Wait for all enabled providers to complete their tasks.

        This method waits for providers with enabled status to finish their tasks and pending request queue.
        """
        for provider in self.providers.values():
            if provider.enabled.is_set():
                await provider.queue.join()
                await provider.pending_request_queue.join()

    def stop(self):
        """
        Stop all running tasks.

        This method cancels all running tasks associated with the Controller.
        """
        for task in self.tasks:
            task.cancel()
