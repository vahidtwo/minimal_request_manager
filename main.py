import asyncio
import random
import time

import questionary

from cli import cli
from controler import Controller
from integration.adaptor import Provider
from log import logger


async def run_job():
    random.seed(0)
    provider_count = int(
        await questionary.text("put your provider count", default="2").ask_async()
    )
    provider_rates = []
    for provider in range(provider_count):
        rate = float(
            await questionary.text(
                f"put your rate for provider[{provider}]", default="2"
            ).ask_async()
        )
        provider_rates.append(rate)
    request_count = int(
        await questionary.text("put your request count", default="10").ask_async()
    )
    logger.info("starting")
    providers = [Provider(f"P{i}", rate) for i, rate in enumerate(provider_rates)]
    handler = Controller(providers=providers)
    handler.new_request_received(
        request_name=f"long request execution time",
        provider=providers[0],
        priority=0,
        execution_after=3,
    )
    handler.new_request_received(
        request_name=f"long request execution time",
        provider=providers[0],
        priority=10,
        execution_after=3,
    )
    start_time = time.perf_counter()
    handler.start()
    for i in range(request_count):
        priority = random.randint(1, 10)
        execution_time = random.choice([0, 2])
        provider = random.choice(providers)
        handler.new_request_received(
            request_name=f"{i}",
            provider=provider,
            priority=priority,
            execution_after=execution_time,
        )
    for provider in providers:
        logger.info(
            f"provider {provider.name}[{provider.rate_limit} r/s] queue have {provider.queue.qsize()} requests"
        )
    await cli(handler, start_time)


if __name__ == "__main__":
    asyncio.run(run_job())
