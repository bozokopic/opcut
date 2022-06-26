from hat import aio


def pytest_configure(config):
    aio.init_asyncio()
