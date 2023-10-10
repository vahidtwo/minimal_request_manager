import pytest

from request_manager import Provider, Controller


@pytest.fixture
def provider1():
    return Provider("test_provider", rate_limit=1.0)


@pytest.fixture
def controller():
    return Controller()
