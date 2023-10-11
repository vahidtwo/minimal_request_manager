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
        """stop controller and exit from cli"""
        self.controller.stop()
        exit(0)


class EnableProviderCommand(Command):
    async def execute(self):
        """enabled the provider to start send request"""
        providers = self.controller.providers
        available_providers = [
            provider.name for provider in providers if not provider.enabled.is_set()
        ]
        if not available_providers:
            questionary.print("No provider is available to start")
            return
        selected_provider_name = await questionary.select(
            "Which provider do you want to start?",
            choices=available_providers,
        ).ask_async()
        provider = self.controller.providers[selected_provider_name]
        provider.start()


class DisableProviderCommand(Command):
    async def execute(self):
        """disable provider to stop send request"""
        providers = self.controller.providers
        available_providers = [
            provider.name for provider in providers if provider.enabled.is_set()
        ]
        if not available_providers:
            questionary.print("No provider is available to stop")
            return
        selected_provider_name = await questionary.select(
            "Which provider do you want to stop?",
            choices=available_providers,
        ).ask_async()
        provider = self.controller.providers[selected_provider_name]
        await provider.stop()


class AddRequestCommand(Command):
    async def execute(self):
        """add request to a provider"""
        providers = self.controller.providers
        if len(providers) == 0:
            questionary.print("No provider is available to add request")
            return
        available_providers = [provider.name for provider in providers]
        priority = int(
            await questionary.text("Put your priority", default="1").ask_async()
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
        """Run the controller to start sending task by added providers and requests"""
        self.controller.start()
        for provider in self.controller.providers:
            logger.info(
                f"provider {provider.name}[{provider.rate_limit} r/s] queue have {provider.queue.qsize()} requests"
            )


class StopCommand(Command):
    async def execute(self):
        """Call the controller to stop sending task on providers"""
        self.controller.stop()


class WizardCommand(Command):
    async def execute(self):
        """simulate whole process of sending request include add request and add provider"""
        random.seed(0)
        create_provider = True
        if len(self.controller.providers) != 0:
            create_provider = await questionary.confirm(
                "create new provider?", default=False
            ).ask_async()
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
            await questionary.text("put your request count", default="50").ask_async()
        )
        logger.info("starting")
        if create_provider:
            for i, rate in zip(
                range(
                    len(self.controller.providers),
                    len(self.controller.providers) + provider_count,
                ),
                provider_rates,
            ):
                self.controller.add_provider(Provider(f"P{i}", rate))

        self.controller.start()
        for _ in range(request_count):
            priority = random.randint(1, 10)
            execution_time = random.choice([0, 2])
            provider = random.choice(list(self.controller.providers))
            self.controller.new_request_received(
                request_name=f"{self.controller.request_counter}",
                provider=provider,
                priority=priority,
                execution_after=execution_time,
            )
        for provider in self.controller.providers:
            logger.info(
                f"provider {provider.name}[{provider.rate_limit} r/s] queue have {provider.queue.qsize()} requests"
            )


class SimulateExampleCommand(Command):
    async def execute(self):
        """simulate whole process of sending request include add request and add provider"""
        logger.info("starting")
        provider1, provider2 = Provider(f"P{1}", 0.2), Provider(f"P{2}", 0.1)
        providers = [provider1, provider2]
        self.controller = Controller(providers=providers)
        self.controller.start()
        self.controller.new_request_received(
            request_name=f"{1}",
            provider=provider1,
            execution_after=1,
        )
        self.controller.new_request_received(
            request_name=f"{2}",
            provider=provider1,
            execution_after=3,
        )
        self.controller.new_request_received(
            request_name=f"{3}",
            provider=provider2,
            execution_after=5,
        )
        self.controller.new_request_received(
            request_name=f"{4}",
            provider=provider2,
            execution_after=7,
        )
        for provider in providers:
            logger.info(
                f"provider {provider.name}[{provider.rate_limit} r/s] queue have {provider.queue.qsize()} requests"
            )
        await self.controller.wait_for_complete()
        self.controller.stop()
        input("Press Enter to continue")


class AddProviderCommand(Command):
    async def execute(self):
        """add provider to my controller"""
        provider_name = await questionary.text(
            "put name of provider", default="P[n]"
        ).ask_async()

        rate_limit = float(
            await questionary.text(
                "put your provider rate-limit request/second", default="10.0"
            ).ask_async()
        )
        self.controller.add_provider(Provider(provider_name, rate_limit))
        questionary.print("Provider added successfully")


class CLI:
    controller = Controller()
    command_mapping = {
        CLIActions.WIZARD: WizardCommand(controller),
        CLIActions.ADD_REQUEST: AddRequestCommand(controller),
        CLIActions.ADD_PROVIDER: AddProviderCommand(controller),
        CLIActions.RUN: RunCommand(controller),
        CLIActions.STOP: StopCommand(controller),
        CLIActions.ENABLE_PROVIDER: EnableProviderCommand(controller),
        CLIActions.DISABLE_PROVIDER: DisableProviderCommand(controller),
        CLIActions.SIMULATE_EXAMPLE: SimulateExampleCommand(controller),
        CLIActions.EXIT: ExitCommand(controller),
    }

    @staticmethod
    async def select_command_form_input() -> CLIActions:
        return await questionary.select(
            "What do you want to do?",
            choices=[action for action in CLIActions],
        ).ask_async()

    @staticmethod
    def show_commands(self):
        questionary.print(
            "What do you want to do?",
            choices=[action for action in CLIActions],
        )

    async def run(self):
        # todo refactor cli for return better response
        while True:
            selected_action = await self.select_command_form_input()

            if selected_action in self.command_mapping:
                command = self.command_mapping[selected_action]
                await command.execute()


def main():
    logger.setLevel(logging.INFO)
    asyncio.run(CLI().run())


if __name__ == "__main__":
    main()
