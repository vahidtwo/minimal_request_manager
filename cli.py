import questionary

from controler import Controller
from integration.utils import CLIActions
from log import logger


class Command:
    def __init__(self, controller: Controller):
        self.controller = controller

    async def execute(self):
        pass


class ExitCommand(Command):
    async def execute(self):
        self.controller.stop()


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


async def cli(controller: Controller):
    command_mapping = {
        CLIActions.EXIT: ExitCommand(controller),
        CLIActions.START_PROVIDER: StartProviderCommand(controller),
        CLIActions.STOP_PROVIDER: StopProviderCommand(controller),
        CLIActions.ADD_REQUEST: AddRequestCommand(controller),
    }

    while True:
        await controller.wait_for_complete()
        input("Press Enter to continue")
        selected_action = await questionary.select(
            "What do you want to do?",
            choices=[action for action in CLIActions],
        ).ask_async()

        if selected_action in command_mapping:
            command = command_mapping[selected_action]
            await command.execute()
