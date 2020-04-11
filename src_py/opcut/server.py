import asyncio
import base64
import functools
import ssl
import urllib.parse

from hat.util import aio
import aiohttp.web

from opcut import common
import opcut.csp
import opcut.output


async def run(json_schema_repo, addr, pem_path, ui_path):

    executor = aio.create_executor()

    addr = urllib.parse.urlparse(addr)
    if addr.scheme == 'https':
        ssl_ctx = ssl.SSLContext(ssl.PROTOCOL_SSLv23)
        ssl_ctx.load_cert_chain(pem_path)
    else:
        ssl_ctx = None

    async def root_handler(request):
        raise aiohttp.web.HTTPFound('/index.html')

    app = aiohttp.web.Application()
    app.add_routes([aiohttp.web.get('/', root_handler),
                    aiohttp.web.post('/calculate', functools.partial(
                        _calculate_handler, json_schema_repo, executor)),
                    aiohttp.web.post('/generate_output', functools.partial(
                        _generate_output_handler, json_schema_repo, executor)),
                    aiohttp.web.static('/', ui_path)])

    runner = aiohttp.web.AppRunner(app)
    try:
        await runner.setup()
        site = aiohttp.web.TCPSite(runner,
                                   host=addr.hostname,
                                   port=addr.port,
                                   ssl_context=ssl_ctx,
                                   shutdown_timeout=0.1)
        await site.start()
        await asyncio.Future()
    finally:
        await runner.cleanup()


async def _calculate_handler(json_schema_repo, executor, request):
    try:
        msg = await request.json()
        json_schema_repo.validate(
            'opcut://messages.yaml#/definitions/calculate/request', msg)
        params = common.json_data_to_params(msg['params'])
        method = common.Method[msg['method']]
        result = await executor(opcut.csp.calculate, params, method)
        result_json_data = common.result_to_json_data(result)
    except Exception:
        result_json_data = None
    return aiohttp.web.json_response({'result': result_json_data})


async def _generate_output_handler(json_schema_repo, executor, request):
    try:
        msg = await request.json()
        json_schema_repo.validate(
            'opcut://messages.yaml#/definitions/generate_output/request', msg)
        result = common.json_data_to_result(msg['result'])
        output_type = common.OutputType[msg['output_type']]
        panel = msg['panel']
        output = await executor(opcut.output.generate_output, result,
                                output_type, panel)
        output_json_data = base64.b64encode(output).decode('utf-8')
    except Exception:
        output_json_data = None
    return aiohttp.web.json_response({'data': output_json_data})
