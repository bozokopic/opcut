import ssl
import contextlib
import asyncio

import aiohttp.web


async def run(addr, pem_path, ui_path):

    if addr.scheme == 'https':
        ssl_ctx = ssl.SSLContext(ssl.PROTOCOL_SSLv23)
        ssl_ctx.load_cert_chain(pem_path)
    else:
        ssl_ctx = None

    app = aiohttp.web.Application()
    app.router.add_route('GET', '/',
                         lambda req: aiohttp.web.HTTPFound('/index.html'))
    app.router.add_static('/', ui_path)
    app_handler = app.make_handler()

    srv = await asyncio.get_event_loop().create_server(
        app_handler, host=addr.hostname, port=addr.port, ssl=ssl_ctx)

    with contextlib.suppress(asyncio.CancelledError):
        await asyncio.Future()

    srv.close()
    await srv.wait_closed()
    await app.shutdown()
    await app_handler.finish_connections(0)
    await app.cleanup()
