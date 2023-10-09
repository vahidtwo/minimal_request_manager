import asyncio
import datetime
import random
from asyncio import PriorityQueue

from integration.adaptor import Request, Provider
from integration.contract import Provider as ProviderProto
from integration.utils import StatusCode
from log import logger


class RequestManager:
    pending_requests: dict[int, PriorityQueue[Request]] = ...

    def __init__(self, providers: list[ProviderProto]):
        self.providers = providers
        self.pending_requests = {id(provider): PriorityQueue() for provider in providers}

    def new_request_received(self, provider: Provider, priority: int, execution_after: datetime.datetime | int = 0):
        request = Request(provider=provider, priority=priority, execution_after=execution_after)
        queue: PriorityQueue
        queue = self.pending_requests[id(provider)]
        queue.put_nowait((request.priority, request))

    @classmethod
    async def _run_requests(cls, queue: PriorityQueue):
        current_time = datetime.datetime.now().strftime("%H:%M:%S")
        request: Request
        _, request = await queue.get()
        if request.is_ready:
            result = await request.provider.send_request()
            msg = "Sending request {} to provider {} with priority {} at {} (Execution time: {})".format(
                request.name, request.provider.name, request.priority, current_time, request.execution_time
            )
            log = "{}\n| {} |\n{}".format("+" * 84, msg, "+" * 84)
            print(log)
            if result.status_code != StatusCode.SUCCESS:
                queue.task_done()

    async def start(self):
        tasks = [asyncio.create_task(self._run_requests(queue)) for queue in self.pending_requests.values()]
        await asyncio.gather(*tasks)


async def main():
    provider_rates = [0.2, 100, 1, 4, 20]
    request_count = 10
    print("starting")
    providers = [Provider(f"P{i}", rate) for i, rate in enumerate(provider_rates)]
    manager = RequestManager(providers=providers)
    await manager.start()
    for i in range(request_count):
        priority = random.randint(1, 10)
        execution_time = random.choice([i for i in range(0, 10, 2)])
        print(f"add request {i} with priority {priority} and execution time {execution_time}")
        manager.new_request_received(
            provider=random.choice(providers), priority=priority, execution_after=execution_time
        )
        await asyncio.sleep(random.randint(1, 3))


if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
