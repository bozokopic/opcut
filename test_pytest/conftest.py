import pytest

from hat import aio


loop = None


@pytest.fixture(scope='session')
def event_loop():
    yield loop
    loop.close()


def pytest_configure(config):
    global loop
    loop = aio.init_asyncio()
