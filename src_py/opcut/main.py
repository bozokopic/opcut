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


params_schema_id: str = 'opcut://opcut.yaml#/definitions/params'
result_schema_id: str = 'opcut://opcut.yaml#/definitions/result'


def _doc_enum_values(enum_cls):
    return ', '.join(str(i.value) for i in enum_cls)


@click.group()
def main():
    """Application main entry point"""


@main.command()
@click.option('--method',
              default=common.Method.FORWARD_GREEDY,
              type=common.Method,
              help=f"calculate method ({_doc_enum_values(common.Method)})")
@click.option('--output',
              default=None,
              metavar='PATH',
              type=Path,
              help=f"result file path ({result_schema_id})")
@click.argument('params',
                required=False,
                default=None,
                metavar='PATH',
                type=Path)
def calculate(method: common.Method,
              output: typing.Optional[Path],
              params: typing.Optional[Path]):
    """Calculate result based on parameters JSON"""
    params = (json.decode_file(params) if params and params != Path('-')
              else json.decode_stream(sys.stdin))
    common.json_schema_repo.validate(params_schema_id, params)
    params = common.params_from_json(params)

    try:
        res = opcut.csp.calculate(params, method)

    except common.UnresolvableError:
        sys.exit(42)

    res = common.result_to_json(res)

    if output and output != Path('-'):
        json.encode_file(res, output)
    else:
        json.encode_stream(res, sys.stdout)


@main.command()
@click.option('--output-type',
              default=common.OutputType.PDF,
              type=common.OutputType,
              help=f"output type ({_doc_enum_values(common.OutputType)})")
@click.option('--panel',
              default=None,
              help="panel identifier")
@click.option('--output',
              default=None,
              metavar='PATH',
              type=Path,
              help="result file path")
@click.argument('result',
                required=False,
                default=None,
                metavar='PATH',
                type=Path)
def generate_output(output_type: common.OutputType,
                    panel: typing.Optional[str],
                    output: typing.Optional[Path],
                    result: typing.Optional[Path]):
    """Generate output based on result JSON"""
    result = (json.decode_file(result) if result and result != Path('-')
              else json.decode_stream(sys.stdin))
    common.json_schema_repo.validate(result_schema_id, result)
    result = common.result_from_json(result)

    out = opcut.output.generate_output(result, output_type, panel)

    if output and output != Path('-'):
        output.write_bytes(out)
    else:
        stdout, sys.stdout = sys.stdout.detach(), None
        stdout.write(out)


@main.command()
@click.option('--host',
              default='0.0.0.0',
              help="listening host name")
@click.option('--port',
              default=8080,
              type=int,
              help="listening TCP port")
@click.option('--log-level',
              default='INFO',
              type=click.Choice(['CRITICAL', 'ERROR', 'WARNING', 'INFO',
                                 'DEBUG', 'NOTSET']),
              help="log level")
def server(host: str,
           port: int,
           log_level: str):
    """Run server"""
    logging.config.dictConfig({
        'version': 1,
        'formatters': {
            'console': {
                'format': "[%(asctime)s %(levelname)s %(name)s] %(message)s"}},
        'handlers': {
            'console': {
                'class': 'logging.StreamHandler',
                'formatter': 'console',
                'level': log_level}},
        'root': {
            'level': log_level,
            'handlers': ['console']},
        'disable_existing_loggers': False})

    async def run():
        server = await opcut.server.create(host, port)

        try:
            await server.wait_closing()

        finally:
            await aio.uncancellable(server.async_close())

    loop = aio.init_asyncio()
    with contextlib.suppress(asyncio.CancelledError):
        aio.run_asyncio(run(), loop=loop)


if __name__ == '__main__':
    sys.argv[0] = 'opcut'
    sys.exit(main())
