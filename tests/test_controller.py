import asyncio

import pytest
import datetime

from tests.fixtures import controller, provider1


class TestController:
    def test_add_provider(self, controller, provider1):
        controller.add_provider(provider1)
        assert "test_provider" in controller.providers

    def test_new_request_received(self, controller, provider1):
        priority = 1
        request_name = "test_request"
        execution_after = datetime.datetime.now() + datetime.timedelta(minutes=10)

        request = controller.new_request_received(
            provider1, priority, execution_after, request_name
        )

        assert request.name == request_name
        assert request.priority == -priority  # Priority should be negated
        assert request.provider == provider1
        assert request.execution_time == execution_after.timestamp()

    @pytest.mark.asyncio
    async def test_start(self, controller, provider1):
        controller.add_provider(provider1)
        controller.start()
        for task in controller.tasks:
            assert not task.done()

    @pytest.mark.asyncio
    async def test_wait_for_complete(self, controller, provider1):
        controller.add_provider(provider1)
        controller.new_request_received(provider1, 1, 0, "test")
        controller.start()

        assert provider1.queue.qsize() == 1
        await controller.wait_for_complete()
        assert provider1.queue.qsize() == 0
        for task in controller.tasks:
            assert not task.done()

    @pytest.mark.asyncio
    async def test_stop(self, controller, provider1):
        controller.add_provider(provider1)
        controller.start()
        controller.stop()
        await asyncio.sleep(1)

        for task in controller.tasks:
            assert task.done()

    @pytest.mark.asyncio
    async def test_not_start_the_not_enabled_provider(self, controller, provider1):
        controller.add_provider(provider1)
        controller.new_request_received(provider1, 1, 0, "test")
        provider1.stop()

        controller.start()
        assert provider1.queue.qsize() == 1
        controller.stop()
        await asyncio.sleep(1)

    @pytest.mark.asyncio
    async def test_do_request_not_enabled_provider_after_enabled(
        self, controller, provider1
    ):
        controller.add_provider(provider1)
        provider1.stop()
        controller.new_request_received(provider1, 1, 0, "test")

        assert provider1.queue.qsize() == 1
        controller.start()
        provider1.start()
        await asyncio.sleep(1)
        assert provider1.queue.qsize() == 0
        controller.stop()
