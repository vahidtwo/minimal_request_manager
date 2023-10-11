import asyncio
import datetime
from asyncio import Task

from .integration import Provider, JobRequest
from .integration.abc import ProviderABC
from .integration.adaptor import ProviderContainer
from .log import logger


class Controller:
    tasks: list[Task]
    providers = dict[str, ProviderABC]
    request_counter = 0

    def __init__(self, providers: list[ProviderABC] | None = None):
        """
        Initialize a Controller object.

        Args:
            providers (list[Provider]): A list of Provider objects to manage.
        """
        self.providers = ProviderContainer(provider_list=providers)
        self.tasks = []

    def add_provider(self, provider: ProviderABC):
        self.providers[provider.name] = provider

    def new_request_received(
        self,
        provider: Provider,
        priority: int = 10,
        execution_after: datetime.datetime | int = 0,
        request_name: str | None = None,
    ) -> JobRequest:
        """
         Create a new job request and add it to the provider's queue.

        Args:
            provider (Provider): The provider to which the job request is associated.
            priority (int): The priority of the job request.
            execution_after (datetime.datetime | int, optional): The time when the job should be executed.
                It can be either a datetime object or an integer representing seconds from the current time.
                Defaults to 0, which means immediate execution.
            request_name (str, optional): A name or identifier for the job request. Defaults to an empty string.

        Returns:
            JobRequest: The created JobRequest object.
        """
        request = JobRequest(
            name=request_name if request_name else f"{self.request_counter}",
            provider=provider,
            priority=priority,
            execution_after=execution_after,
        )
        provider.queue.put_nowait((request.priority, request))
        logger.info(f"added {request}")
        self.request_counter += 1
        return request

    def start(self):
        """
        Start the providers' tasks.
        This method creates tasks for each provider to run concurrently
        """
        self.tasks = [
            asyncio.create_task(provider.run()) for provider in self.providers
        ]

    async def wait_for_complete(self):
        """
        Wait for all enabled providers to complete their tasks.

        This method waits for providers with enabled status to finish their tasks and pending request queue.
        """
        for provider in self.providers:
            if provider.enabled.is_set():
                await provider.pending_request_queue.join()
                await provider.queue.join()

    def stop(self):
        """
        Stop all running tasks.

        This method cancels all running tasks associated with the Controller.
        """
        for task in self.tasks:
            task.cancel()
