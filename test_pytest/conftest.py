import asyncio

import pytest

from hat import aio


@pytest.fixture(scope='session')
def event_loop():
    loop = asyncio.get_event_loop()
    yield loop
    loop.close()


def pytest_configure(config):
    aio.init_asyncio()
