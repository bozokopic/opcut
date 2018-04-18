import ssl
import contextlib
import asyncio
import functools
import base64

import aiohttp.web

from opcut import util
from opcut import common
import opcut.json_validator
import opcut.csp
import opcut.output


async def run(addr, pem_path, ui_path):

    executor = util.create_async_executor()

    if addr.scheme == 'https':
        ssl_ctx = ssl.SSLContext(ssl.PROTOCOL_SSLv23)
        ssl_ctx.load_cert_chain(pem_path)
    else:
        ssl_ctx = None

    app = aiohttp.web.Application()
    app.router.add_route('GET', '/',
                         lambda req: aiohttp.web.HTTPFound('/index.html'))
    app.router.add_route('POST', '/calculate',
                         functools.partial(_calculate_handler, executor))
    app.router.add_route('POST', '/generate_output',
                         functools.partial(_generate_output_handler, executor))
    app.router.add_static('/', ui_path)
    app_handler = app.make_handler()

    srv = await asyncio.get_event_loop().create_server(
        app_handler, host=addr.hostname, port=addr.port, ssl=ssl_ctx)

    with contextlib.suppress(asyncio.CancelledError):
        await asyncio.Future()

    srv.close()
    await srv.wait_closed()
    await app.shutdown()
    await app_handler.finish_connections(0.1)
    await app.cleanup()


async def _calculate_handler(executor, request):
    try:
        msg = await request.json()
        opcut.json_validator.validate(
            msg, 'opcut://messages.yaml#/definitions/calculate/request')
        params = common.json_data_to_params(msg['params'])
        method = common.Method[msg['method']]
        result = await executor(_ext_calculate, params, method)
        result_json_data = common.result_to_json_data(result)
    except asyncio.CancelledError:
        raise
    except Exception as e:
        result_json_data = None
    return aiohttp.web.json_response({'result': result_json_data})


async def _generate_output_handler(executor, request):
    try:
        msg = await request.json()
        opcut.json_validator.validate(
            msg, 'opcut://messages.yaml#/definitions/generate_output/request')
        result = common.json_data_to_result(msg['result'])
        output_type = common.OutputType[msg['output_type']]
        panel = msg['panel']
        output = await executor(_ext_generate_output, result, output_type,
                                panel)
        output_json_data = base64.b64encode(output).decode('utf-8')
    except asyncio.CancelledError:
        raise
    except Exception as e:
        output_json_data = None
    return aiohttp.web.json_response({'data': output_json_data})


def _ext_calculate(params, method):
    return opcut.csp.calculate(params, method)


def _ext_generate_output(result, output_type, panel):
    return opcut.output.generate_output(result, output_type, panel)
