import contextlib
import asyncio
import sys
import collections
import concurrent


def namedtuple(name, *props):
    """Create documented namedtuple

    Args:
        name (Union[str,Tuple[str,str]]):
            named tuple's name or named tuple's name with documentation
        props (Iterable[Union[str,Tuple[str,str],Tuple[str,str,Any]]]):
            named tuple' properties with optional documentation and
            optional default value

    Returns:
        class implementing collections.namedtuple

    """
    props = [(i, None) if isinstance(i, str) else list(i) for i in props]
    cls = collections.namedtuple(name if isinstance(name, str) else name[0],
                                 [i[0] for i in props])
    default_values = []
    for i in props:
        if default_values and len(i) < 3:
            raise Exception("property with default value not at end")
        if len(i) > 2:
            default_values.append(i[2])
    if default_values:
        cls.__new__.__defaults__ = tuple(default_values)
    if not isinstance(name, str) and name[1]:
        cls.__doc__ = name[1]
    for i in props:
        if i[1]:
            getattr(cls, i[0]).__doc__ = i[1]
    try:
        cls.__module__ = sys._getframe(1).f_globals.get('__name__', '__main__')
    except (AttributeError, ValueError):
        pass
    return cls


def run_until_complete_without_interrupt(future, loop=None):
    """Run event loop until future or coroutine is done

    Args:
        future (Awaitable): future or coroutine
        loop (Optional[asyncio.AbstractEventLoop]): asyncio loop

    Returns:
        Any: provided future's result

    KeyboardInterrupt is suppressed (while event loop is running) and is mapped
    to single cancelation of running task. If multipple KeyboardInterrupts
    occur, task is cancelled only once.

    """
    if not loop:
        loop = asyncio.get_event_loop()

    async def ping_loop():
        with contextlib.suppress(asyncio.CancelledError):
            while True:
                await asyncio.sleep(1, loop=loop)

    task = asyncio.ensure_future(future, loop=loop)
    if sys.platform == 'win32':
        ping_loop_task = asyncio.ensure_future(ping_loop(), loop=loop)
    with contextlib.suppress(KeyboardInterrupt):
        loop.run_until_complete(task)
    loop.call_soon(task.cancel)
    if sys.platform == 'win32':
        loop.call_soon(ping_loop_task.cancel)
    while not task.done():
        with contextlib.suppress(KeyboardInterrupt):
            loop.run_until_complete(task)
    if sys.platform == 'win32':
        while not ping_loop_task.done():
            with contextlib.suppress(KeyboardInterrupt):
                loop.run_until_complete(ping_loop_task)
    return task.result()


def create_async_executor(*args,
                          executor_cls=concurrent.futures.ThreadPoolExecutor,
                          loop=None):
    """Create run_in_executor wrapper

    Args:
        args (Any): executor init args
        executor_cls (Type): executor class
        loop (Optional[asyncio.AbstractEventLoop]): asyncio loop

    Returns:
        Callable[[Callable,...],Any]: coroutine accepting function and it's
            arguments and returning function call result

    """
    executor = executor_cls(*args)

    async def executor_wrapper(fn, *fn_args):
        _loop = loop if loop else asyncio.get_event_loop()
        return await _loop.run_in_executor(executor, fn, *fn_args)

    return executor_wrapper
