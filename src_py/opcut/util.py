import contextlib
import asyncio
import sys


def run_until_complete_without_interrupt(future):
    """Run event loop until future or coroutine is done

    Args:
        future (Awaitable): future or coroutine

    Returns:
        Any: provided future's result

    KeyboardInterrupt is suppressed (while event loop is running) and is mapped
    to single cancelation of running task. If multipple KeyboardInterrupts
    occur, task is canceled only once.

    """
    async def ping_loop():
        with contextlib.suppress(asyncio.CancelledError):
            while True:
                await asyncio.sleep(1)

    task = asyncio.ensure_future(future)
    if sys.platform == 'win32':
        ping_loop_task = asyncio.ensure_future(ping_loop())
    with contextlib.suppress(KeyboardInterrupt):
        asyncio.get_event_loop().run_until_complete(task)
    asyncio.get_event_loop().call_soon(task.cancel)
    if sys.platform == 'win32':
        asyncio.get_event_loop().call_soon(ping_loop_task.cancel)
    while not task.done():
        with contextlib.suppress(KeyboardInterrupt):
            asyncio.get_event_loop().run_until_complete(task)
    if sys.platform == 'win32':
        while not ping_loop_task.done():
            with contextlib.suppress(KeyboardInterrupt):
                asyncio.get_event_loop().run_until_complete(ping_loop_task)
    return task.result()
