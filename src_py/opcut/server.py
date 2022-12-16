import asyncio
import contextlib
import importlib.resources
import subprocess
import sys

from hat import aio
from hat import json
import aiohttp.web

from opcut import common


async def create(host: str,
                 port: int,
                 timeout: float
                 ) -> 'Server':
    server = Server()
    server._timeout = timeout
    server._async_group = aio.Group()

    try:
        exit_stack = contextlib.ExitStack()
        static_dir = exit_stack.enter_context(
            importlib.resources.path(__package__, 'ui'))
        server.async_group.spawn(aio.call_on_cancel, exit_stack.close)

        app = aiohttp.web.Application()
        app.add_routes([
            aiohttp.web.get('/', server._root_handler),
            aiohttp.web.post('/calculate', server._calculate_handler),
            aiohttp.web.post('/generate', server._generate_handler),
            aiohttp.web.static('/', static_dir)])

        runner = aiohttp.web.AppRunner(app)
        await runner.setup()
        server.async_group.spawn(aio.call_on_cancel, runner.cleanup)

        site = aiohttp.web.TCPSite(runner=runner,
                                   host=host,
                                   port=port,
                                   shutdown_timeout=0.1,
                                   reuse_address=True)
        await site.start()

    except BaseException:
        await aio.uncancellable(server.async_close())
        raise

    return server


class Server(aio.Resource):

    @property
    def async_group(self):
        return self._async_group

    async def _root_handler(self, request):
        raise aiohttp.web.HTTPFound('/index.html')

    async def _calculate_handler(self, request):
        try:
            data = await request.json()
            common.json_schema_repo.validate(
                'opcut://opcut.yaml#/definitions/params', data)

        except Exception:
            return aiohttp.web.Response(status=400,
                                        text="Invalid request")

        method = common.Method(request.query['method'])
        params = common.params_from_json(data)

        try:
            result = await asyncio.wait_for(_calculate(method, params),
                                            self._timeout)
            return aiohttp.web.json_response(result)

        except asyncio.TimeoutError:
            return aiohttp.web.Response(status=400,
                                        text='Request timeout')

        except common.UnresolvableError:
            return aiohttp.web.Response(status=400,
                                        text='Result is not solvable')

    async def _generate_handler(self, request):
        try:
            data = await request.json()
            common.json_schema_repo.validate(
                'opcut://opcut.yaml#/definitions/result', data)

        except Exception:
            return aiohttp.web.Response(status=400,
                                        text="Invalid request")

        output_format = common.OutputFormat(request.query['output_format'])
        panel = request.query.get('panel')
        result = common.result_from_json(data)

        try:
            output = await asyncio.wait_for(
                _generate(output_format, panel, result), self._timeout)

        except asyncio.TimeoutError:
            return aiohttp.web.Response(status=400,
                                        text='Request timeout')

        if output_format == common.OutputFormat.PDF:
            content_type = 'application/pdf'

        elif output_format == common.OutputFormat.SVG:
            content_type = 'image/svg+xml'

        else:
            raise Exception('unsupported output type')

        return aiohttp.web.Response(body=output,
                                    content_type=content_type)


async def _calculate(method, params):
    args = [sys.executable, '-m', 'opcut', 'calculate',
            '--method', method.value]
    stdint_data = json.encode(common.params_to_json(params)).encode('utf-8')

    p = await asyncio.create_subprocess_exec(*args,
                                             stdin=subprocess.PIPE,
                                             stdout=subprocess.PIPE,
                                             stderr=subprocess.PIPE)

    stderr_data = None
    try:
        stdout_data, stderr_data = await p.communicate(stdint_data)

    finally:
        if p.returncode is None:
            p.terminate()

    if p.returncode == 0:
        return json.decode(stdout_data.decode('utf-8'))

    if p.returncode == 42:
        raise common.UnresolvableError()

    if not stderr_data:
        raise Exception()

    raise Exception(stderr_data.decode('utf-8'))


async def _generate(output_format, panel, result):
    args = [sys.executable, '-m', 'opcut', 'generate',
            '--output-format', output_format.value,
            *(['--panel', panel] if panel else [])]
    stdint_data = json.encode(common.result_to_json(result)).encode('utf-8')

    p = await asyncio.create_subprocess_exec(*args,
                                             stdin=subprocess.PIPE,
                                             stdout=subprocess.PIPE,
                                             stderr=subprocess.PIPE)

    stderr_data = None
    try:
        stdout_data, stderr_data = await p.communicate(stdint_data)

    finally:
        if p.returncode is None:
            p.terminate()

    if p.returncode == 0:
        return stdout_data

    if not stderr_data:
        raise Exception()

    raise Exception(stderr_data.decode('utf-8'))
