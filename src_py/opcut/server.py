from pathlib import Path

from hat import aio
import aiohttp.web

from opcut import common
import opcut.csp
import opcut.output


static_dir: Path = common.package_path / 'ui'


async def create(host: str,
                 port: int
                 ) -> 'Server':
    server = Server()
    server._async_group = aio.Group()
    server._executor = aio.create_executor()

    app = aiohttp.web.Application()
    app.add_routes([
        aiohttp.web.get('/', server._root_handler),
        aiohttp.web.post('/calculate', server._calculate_handler),
        aiohttp.web.post('/generate_output', server._generate_output_handler),
        aiohttp.web.static('/', static_dir)])

    runner = aiohttp.web.AppRunner(app)
    await runner.setup()
    server.async_group.spawn(aio.call_on_cancel, runner.cleanup)

    try:
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
        data = await request.json()
        common.json_schema_repo.validate(
            'opcut://opcut.yaml#/definitions/params', data)

        method = common.Method(request.query['method'])
        params = common.params_from_json(data)

        result = await self._executor(opcut.csp.calculate, params, method)

        return aiohttp.web.json_response(common.result_to_json(result))

    async def _generate_output_handler(self, request):
        data = await request.json()
        common.json_schema_repo.validate(
            'opcut://opcut.yaml#/definitions/result', data)

        output_type = common.OutputType(request.query['output_type'])
        panel = request.query.get('panel')
        result = common.result_from_json(data)

        output = await self._executor(opcut.output.generate_output, result,
                                      output_type, panel)

        if output_type == common.OutputType.PDF:
            content_type = 'application/pdf'

        elif output_type == common.OutputType.SVG:
            content_type = 'image/svg+xml'

        else:
            raise Exception('unsupported output type')

        return aiohttp.web.Response(body=output,
                                    content_type=content_type)
