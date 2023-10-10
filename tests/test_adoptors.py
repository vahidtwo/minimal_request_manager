import datetime
import time
from unittest.mock import Mock, patch

import pytest

from request_manager import JobRequest, Response, StatusCode
from tests.fixtures import provider1


class TestJobRequest:
    def test_is_ready(self, provider1):
        priority = 1
        execution_after = datetime.datetime.now() + datetime.timedelta(minutes=1)
        name = "test_request"

        request = JobRequest(provider1, priority, execution_after, name)
        assert request.is_ready is False

        execution_after = datetime.datetime.now() - datetime.timedelta(minutes=1)
        request = JobRequest(provider1, priority, execution_after, name)
        assert request.is_ready is True


class TestProvider:
    @pytest.mark.asyncio
    async def test_wait_for_rate_limit(self, provider1):
        provider1.last_request_time = time.time()
        provider1.rate_limit = 2
        start = time.time()
        await provider1.wait_for_rate_limit()
        end = time.time()
        assert bool(0.49 < (end - start) < 0.51)

    @pytest.mark.asyncio
    async def test_send_request(self, provider1):
        request = Mock()
        request.name = "test_request"
        response = await provider1.send_request(request)
        assert isinstance(response, Response)
        assert response.status_code == StatusCode.SUCCESS

    @pytest.mark.asyncio
    async def test_check_pending_request(self, provider1):
        request = Mock()
        request.name = "test_request"
        request.is_ready = True

        provider1.pending_request_queue.put_nowait((1, request))
        await provider1.check_pending_request()
        assert provider1.queue.qsize() == 1
        assert provider1.pending_request_queue.qsize() == 0

    @pytest.mark.asyncio
    async def test_run(self, provider1):
        request = JobRequest(provider1, 1, 0, "test")
        provider1.queue.put_nowait((1, request))
        provider1.enabled.set()

        async def fake_send_request(request):
            return Response(status_code=StatusCode.SUCCESS, data={"message": "done"})

        with patch.object(provider1, "send_request", side_effect=fake_send_request):
            assert provider1.queue.qsize() == 1
            await provider1._run_job()
            assert provider1.queue.qsize() == 0

    @pytest.mark.asyncio
    async def test_stop(self, provider1):
        provider1.enabled.set()
        await provider1.stop()
        assert not provider1.enabled.is_set()
