import time

import questionary

from controler import Controller
from integration.utils import CLIActions
from log import logger


async def cli(controller: Controller, start_time: time.perf_counter) -> None:
    is_user_want_end = False
    providers = controller.providers.values()
    while is_user_want_end is False:
        await controller.wait_for_complete()
        end_time = time.perf_counter()
        logger.info(f"total execution time is {end_time - start_time} seconds")
        input("press enter to continue")
        selected_action = await questionary.select(
            "What do you want to do?",
            choices=[action for action in CLIActions],
        ).ask_async()
        if selected_action == CLIActions.EXIT:
            is_user_want_end = True
            controller.stop()
        elif selected_action == CLIActions.START_PROVIDER:
            available_providers = [
                provider.name
                for provider in providers
                if provider.enabled.is_set() is False
            ]
            if len(available_providers) == 0:
                logger.info("no provider is available to start")
            selected_provider_name = await questionary.select(
                "Which provider do you want to start?",
                choices=available_providers,
            ).ask_async()
            provider = controller.providers[selected_provider_name]
            provider.start()
        elif selected_action == CLIActions.STOP_PROVIDER:
            available_providers = [
                provider.name
                for provider in providers
                if provider.enabled.is_set() is True
            ]
            if len(available_providers) == 0:
                logger.info("no provider is available to stop")
            selected_provider_name = await questionary.select(
                "Which provider do you want to stop?",
                choices=available_providers,
            ).ask_async()
            provider = controller.providers[selected_provider_name]
            await provider.stop()
        elif selected_action == CLIActions.ADD_REQUEST:
            available_providers = [
                provider.name
                for provider in providers
                if provider.enabled.is_set() is True
            ]
            priority = int(
                await questionary.text("put your priority", default="1").ask_async()
            )
            execution_time = int(
                await questionary.text(
                    "put your execution time in seconds", default="0"
                ).ask_async()
            )
            selected_provider_name = await questionary.select(
                "Which provider do you want to use?", choices=available_providers
            ).ask_async()

            provider = controller.providers[selected_provider_name]
            logger.info(
                f"add request/provider Provider[provider.name] "
                f"with priority {priority} and execution time {execution_time}"
            )
            controller.new_request_received(
                provider=provider,
                priority=priority,
                execution_after=execution_time,
            )
