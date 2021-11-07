from pathlib import Path
import asyncio
import contextlib
import logging.config
import sys
import typing

from hat import aio
from hat import json
import click

from opcut import common
import opcut.csp
import opcut.output
import opcut.server


log_schema_id: str = 'hat-json://logging.yaml#'
params_schema_id: str = 'opcut://opcut.yaml#/definitions/params'
result_schema_id: str = 'opcut://opcut.yaml#/definitions/result'


@click.group()
@click.option('--log',
              default=None,
              metavar='PATH',
              type=Path,
              help=f"logging configuration file path {log_schema_id}")
def main(log: typing.Optional[Path]):
    """Application main entry point"""
    if not log:
        return

    log_conf = json.decode_file(log)
    common.json_schema_repo.validate(log_schema_id, log_conf)
    logging.config.dictConfig(log_conf)


@main.command()
@click.option('--method',
              default=common.Method.FORWARD_GREEDY,
              type=common.Method,
              help="calculate method")
@click.option('--params',
              default=None,
              metavar='PATH',
              type=Path,
              help=f"calculate parameters file path ({params_schema_id})")
@click.option('--result',
              default=None,
              metavar='PATH',
              type=Path,
              help=f"result file path ({result_schema_id})")
def calculate(method: common.Method,
              params: typing.Optional[Path],
              result: typing.Optional[Path]):
    """Calculate result"""
    params = (json.decode_file(params) if params
              else json.decode_stream(sys.stdin))
    common.json_schema_repo.validate(params_schema_id, params)
    params = common.params_from_json(params)

    res = opcut.csp.calculate(params, method)
    res = common.result_to_json(res)

    if result:
        json.encode_file(res, result)
    else:
        json.encode_stream(res, sys.stdout)


@main.command()
@click.option('--output-type',
              default=common.OutputType.PDF,
              type=common.OutputType,
              help="output type")
@click.option('--panel',
              default=None,
              help="panel identifier")
@click.option('--result',
              default=None,
              metavar='PATH',
              type=Path,
              help=f"result file path ({result_schema_id})")
@click.option('--output',
              default=None,
              metavar='PATH',
              type=Path,
              help="result file path")
def generate_output(output_type: common.OutputType,
                    panel: typing.Optional[str],
                    result: typing.Optional[Path],
                    output: typing.Optional[Path]):
    """Generate output"""
    result = (json.decode_file(result) if result
              else json.decode_stream(sys.stdin))
    common.json_schema_repo.validate(result_schema_id, result)
    result = common.result_from_json(result)

    out = opcut.output.generate_output(result, output_type, panel)

    if output:
        out.write_bytes(out)
    else:
        sys.stdout.detach().write(out)


@main.command()
@click.option('--host',
              default='0.0.0.0',
              help="listening host name")
@click.option('--port',
              default=8080,
              type=int,
              help="listening TCP port")
def server(host: str,
           port: int):
    """Run server"""
    aio.init_asyncio()

    async def run():
        server = await opcut.server.create(host, port)

        try:
            await server.wait_closing()

        finally:
            await aio.uncancellable(server.async_close())

    with contextlib.suppress(asyncio.CancelledError):
        aio.run_asyncio(run())


if __name__ == '__main__':
    sys.argv[0] = 'opcut'
    sys.exit(main())
