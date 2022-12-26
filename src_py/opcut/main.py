from pathlib import Path
import argparse
import asyncio
import contextlib
import logging.config
import sys
import typing

from hat import aio
from hat import json

from opcut import common
import opcut.calculate
import opcut.generate
import opcut.server


params_schema_id: str = 'opcut://opcut.yaml#/definitions/params'
result_schema_id: str = 'opcut://opcut.yaml#/definitions/result'


def create_argument_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description='cutting stock problem optimizer with web interface',
        epilog='For more options, run "%(prog)s <action> --help"')
    subparsers = parser.add_subparsers(dest='action',
                                       required=True)

    def enum_values(enum_cls):
        return ', '.join(str(i.value) for i in enum_cls)

    calculate = subparsers.add_parser(
        'calculate',
        help='Outputs the optimal stock cuts as a text file.')
    calculate.add_argument(
        '--method', metavar='METHOD', type=common.Method,
        default=common.Method.FORWARD_GREEDY,
        help=f"calculate method ({enum_values(common.Method)})")
    calculate.add_argument(
        '--input-format', metavar='FORMAT', type=json.Format, default=None,
        help=f"input params format ({enum_values(json.Format)})")
    calculate.add_argument(
        '--output-format', metavar='FORMAT', type=json.Format, default=None,
        help=f"output result format ({enum_values(json.Format)})")
    calculate.add_argument(
        '--output', metavar='PATH', type=Path, default=Path('-'),
        help=f"output result file path or - for stdout ({result_schema_id})")
    calculate.add_argument(
        'params', type=Path, default=Path('-'), nargs='?',
        help=f"input params file path or - for stdin ({params_schema_id})")

    generate = subparsers.add_parser(
        'generate',
        help='Renders a cut list as an image file.')
    generate.add_argument(
        '--input-format', metavar='FORMAT', type=json.Format, default=None,
        help=f"input result format ({enum_values(json.Format)})")
    generate.add_argument(
        '--output-format', metavar='FORMAT', type=common.OutputFormat,
        default=common.OutputFormat.PDF,
        help=f"output format ({enum_values(common.OutputFormat)})")
    generate.add_argument(
        '--panel', metavar='PANEL', default=None,
        help="panel identifier")
    generate.add_argument(
        '--output', metavar='PATH', type=Path, default=Path('-'),
        help="output file path or - for stdout")
    generate.add_argument(
        'result', type=Path, default=Path('-'), nargs='?',
        help=f"input result file path or - for stdin ({result_schema_id})")

    server = subparsers.add_parser(
        'server',
        help='Run a web server with user interface')
    server.add_argument(
        '--host', metavar='HOST', default='0.0.0.0',
        help="listening host name (default 0.0.0.0)")
    server.add_argument(
        '--port', metavar='PORT', type=int, default=8080,
        help="listening TCP port (default 8080)")
    server.add_argument(
        '--timeout', metavar='T', type=float, default=300,
        help="single request timeout in seconds (default 300)")
    server.add_argument(
        '--log-level', metavar='LEVEL', default='info',
        choices=['critical', 'error', 'warning', 'info', 'debug', 'notset'],
        help="log level (default info)")

    return parser


def main():
    parser = create_argument_parser()
    args = parser.parse_args()

    if args.action == 'calculate':
        calculate(method=args.method,
                  input_format=args.input_format,
                  output_format=args.output_format,
                  result_path=args.output,
                  params_path=args.params)

    elif args.action == 'generate':
        generate(input_format=args.input_format,
                 output_format=args.output_format,
                 panel_id=args.panel,
                 output_path=args.output,
                 result_path=args.result)

    elif args.action == 'server':
        server(host=args.host,
               port=args.port,
               timeout=args.timeout,
               log_level=args.log_level)

    else:
        raise ValueError('unsupported action')


def calculate(method: common.Method,
              input_format: typing.Optional[json.Format],
              output_format: typing.Optional[json.Format],
              result_path: Path,
              params_path: Path):
    if input_format is None and params_path == Path('-'):
        input_format = json.Format.JSON

    if output_format is None and result_path == Path('-'):
        output_format = json.Format.JSON

    params_json = (json.decode_stream(sys.stdin, input_format)
                   if params_path == Path('-')
                   else json.decode_file(params_path, input_format))

    common.json_schema_repo.validate(params_schema_id, params_json)
    params = common.params_from_json(params_json)

    try:
        result = opcut.calculate.calculate(method=method,
                                           params=params)

    except common.UnresolvableError:
        sys.exit(42)

    result_json = common.result_to_json(result)

    if result_path == Path('-'):
        json.encode_stream(result_json, sys.stdout, output_format)
    else:
        json.encode_file(result_json, result_path, output_format)


def generate(input_format: typing.Optional[json.Format],
             output_format: common.OutputFormat,
             panel_id: typing.Optional[str],
             output_path: Path,
             result_path: Path):
    if input_format is None and result_path == Path('-'):
        input_format = json.Format.JSON

    result_json = (json.decode_stream(sys.stdin, input_format)
                   if result_path == Path('-')
                   else json.decode_file(result_path, input_format))

    common.json_schema_repo.validate(result_schema_id, result_json)
    result = common.result_from_json(result_json)

    data = opcut.generate.generate(result=result,
                                   output_format=output_format,
                                   panel_id=panel_id)

    if output_path == Path('-'):
        stdout, sys.stdout = sys.stdout.detach(), None
        stdout.write(data)
    else:
        output_path.write_bytes(data)


def server(host: str,
           port: int,
           timeout: float,
           log_level: str):
    logging.config.dictConfig({
        'version': 1,
        'formatters': {
            'console': {
                'format': "[%(asctime)s %(levelname)s %(name)s] %(message)s"}},
        'handlers': {
            'console': {
                'class': 'logging.StreamHandler',
                'formatter': 'console',
                'level': log_level.upper()}},
        'root': {
            'level': log_level.upper(),
            'handlers': ['console']},
        'disable_existing_loggers': False})

    async def run():
        server = await opcut.server.create(host=host,
                                           port=port,
                                           timeout=timeout)

        try:
            await server.wait_closing()

        finally:
            await aio.uncancellable(server.async_close())

    aio.init_asyncio()
    with contextlib.suppress(asyncio.CancelledError):
        aio.run_asyncio(run())


if __name__ == '__main__':
    sys.argv[0] = 'opcut'
    sys.exit(main())
