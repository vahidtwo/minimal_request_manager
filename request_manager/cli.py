import asyncio
import logging
import random

import questionary

from .controller import Controller
from .integration import Provider
from .integration.utils import CLIActions
from .log import logger


class Command:
    def __init__(self, controller: Controller):
        self.controller = controller

    async def execute(self):
        pass


class ExitCommand(Command):
    async def execute(self):
        self.controller.stop()
        exit(0)


class StartProviderCommand(Command):
    async def execute(self):
        providers = self.controller.providers.values()
        available_providers = [
            provider.name for provider in providers if not provider.enabled.is_set()
        ]
        if not available_providers:
            logger.info("No provider is available to start")
        else:
            selected_provider_name = await questionary.select(
                "Which provider do you want to start?",
                choices=available_providers,
            ).ask_async()
            provider = self.controller.providers[selected_provider_name]
            provider.start()


class StopProviderCommand(Command):
    async def execute(self):
        providers = self.controller.providers.values()
        available_providers = [
            provider.name for provider in providers if provider.enabled.is_set()
        ]
        if not available_providers:
            logger.info("No provider is available to stop")
        else:
            selected_provider_name = await questionary.select(
                "Which provider do you want to stop?",
                choices=available_providers,
            ).ask_async()
            provider = self.controller.providers[selected_provider_name]
            provider.stop()


class AddRequestCommand(Command):
    async def execute(self):
        providers = self.controller.providers.values()
        available_providers = [
            provider.name for provider in providers if provider.enabled.is_set()
        ]
        priority = int(
            questionary.text("Put your priority", default="1").ask_async().result()
        )
        execution_time = int(
            await questionary.text(
                "Put your execution time in seconds", default="0"
            ).ask_async()
        )
        selected_provider_name = await questionary.select(
            "Which provider do you want to use?", choices=available_providers
        ).ask_async()

        provider = self.controller.providers[selected_provider_name]
        logger.info(
            f"Add request/provider Provider[{provider.name}] "
            f"with priority {priority} and execution time {execution_time}"
        )
        self.controller.new_request_received(
            provider=provider,
            priority=priority,
            execution_after=execution_time,
        )


class RunCommand(Command):
    async def execute(self):
        self.controller.start()
        for provider in self.controller.providers:
            logger.info(
                f"provider {provider.name}[{provider.rate_limit} r/s] queue have {provider.queue.qsize()} requests"
            )
        await self.controller.wait_for_complete()


class SimulateCommand(Command):
    async def execute(self):
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
        controller = Controller(providers=providers)
        controller.new_request_received(
            request_name=f"long request execution time",
            provider=providers[0],
            priority=0,
            execution_after=3,
        )
        controller.new_request_received(
            request_name=f"long request execution time",
            provider=providers[0],
            priority=10,
            execution_after=3,
        )
        controller.start()
        for i in range(request_count):
            priority = random.randint(1, 10)
            execution_time = random.choice([0, 2])
            provider = random.choice(providers)
            controller.new_request_received(
                request_name=f"{i}",
                provider=provider,
                priority=priority,
                execution_after=execution_time,
            )
        for provider in providers:
            logger.info(
                f"provider {provider.name}[{provider.rate_limit} r/s] queue have {provider.queue.qsize()} requests"
            )
        await controller.wait_for_complete()


class AddProviderCommand(Command):
    async def execute(self):
        provider_name = await questionary.text(
            "put name of provider", default="P[n]"
        ).ask_async()

        rate_limit = float(
            await questionary.text(
                "put your provider rate-limit request/second", default="10.0"
            ).ask_async()
        )
        self.controller.add_provider(Provider(provider_name, rate_limit))


async def cli(controller: Controller | None = None):
    if controller is None:
        controller = Controller()
    command_mapping = {
        CLIActions.SIMULATE: SimulateCommand(controller),
        CLIActions.RUN: RunCommand(controller),
        CLIActions.START_PROVIDER: StartProviderCommand(controller),
        CLIActions.STOP_PROVIDER: StopProviderCommand(controller),
        CLIActions.ADD_REQUEST: AddRequestCommand(controller),
        CLIActions.ADD_PROVIDER: AddProviderCommand(controller),
        CLIActions.EXIT: ExitCommand(controller),
    }

    while True:
        selected_action = await questionary.select(
            "What do you want to do?",
            choices=[action for action in CLIActions],
        ).ask_async()

        if selected_action in command_mapping:
            command = command_mapping[selected_action]
            await command.execute()
        await controller.wait_for_complete()
        input("Press Enter to continue")


def main():
    logger.setLevel(logging.INFO)
    asyncio.run(cli())
