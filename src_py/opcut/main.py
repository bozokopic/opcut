from pathlib import Path
import argparse
import asyncio
import contextlib
import logging.config
import sys

from hat import util
from hat.util import aio
from hat.util import json

from opcut import common
import opcut.csp
import opcut.output
import opcut.server


package_path = Path(__file__).parent

default_ui_path = package_path / 'ui'
default_schemas_json_path = package_path / 'schemas_json'


def main():
    """Application main entry point"""
    args = _create_parser().parse_args()

    json_schema_repo = json.SchemaRepository(json.default_schemas_json_path,
                                             args.schemas_json_path)

    if args.log_conf_path:
        log_conf = json.decode_file(args.log_conf_path)
        json_schema_repo.validate('hat://logging.yaml#', log_conf)
        logging.config.dictConfig(log_conf)

    if args.action == 'calculate':
        calculate(json_schema_repo, args.params_path, args.method,
                  args.result_path, args.output_path, args.output_type,
                  args.output_panel_id, args.output_path)

    elif args.action == 'output':
        output(json_schema_repo, args.output_path, args.result_path,
               args.output_type, args.output_panel_id, args.output_path)

    else:
        server(json_schema_repo, args.addr, args.pem_path, args.ui_path)


def server(json_schema_repo, addr, ui_pem_path, ui_path):
    """Server main entry point"""
    aio.init_asyncio()
    with contextlib.suppress(asyncio.CancelledError):
        aio.run_asyncio(
            opcut.server.run(json_schema_repo, addr, ui_pem_path, ui_path))


def calculate(json_schema_repo, params_path, method, result_path, output_path,
              output_type, output_panel_id):
    """Calculate result and generate outputs"""
    params_json_data = json.decode_file(params_path)
    opcut.json_validator.validate('opcut://params.yaml#', params_json_data)
    params = common.json_data_to_params(params_json_data)
    result = opcut.csp.calculate(params, method)
    result_json_data = common.result_to_json_data(result)
    json.encode_file(result_json_data, result_path)
    if output_path:
        output(json_schema_repo, output_path, result_path, output_type,
               output_panel_id)


def output(json_schema_repo, output_path, result_path, output_type,
           output_panel_id):
    """Generate outputs based on calculation result"""
    result_json_data = json.decode_file(result_path)
    json_schema_repo.validate('opcut://result.yaml#', result_json_data)
    result = common.json_data_to_result(result_json_data)
    output_bytes = opcut.output.generate_output(result, output_type,
                                                output_panel_id)
    with open(output_path, 'wb') as f:
        f.write(output_bytes)


def _create_parser():
    parser = argparse.ArgumentParser(prog='opcut')
    parser.add_argument(
        '--log', default=None, metavar='path', dest='log_conf_path',
        action=util.EnvPathArgParseAction,
        help="logging configuration")
    subparsers = parser.add_subparsers(title='actions', dest='action')

    server = subparsers.add_parser('server', help='run web server')
    server.add_argument(
        '--addr', default='http://0.0.0.0:8080', metavar='addr', dest='addr',
        help="address of listening web ui socket formated as "
             "'<type>://<host>:<port>' - <type> is 'http' or 'https'; "
             "<host> is hostname; <port> is tcp port number "
             "(default http://0.0.0.0:8080)")
    server.add_argument(
        '--pem', default=None, metavar='path', dest='pem_path',
        action=util.EnvPathArgParseAction,
        help="web front-end pem file path - required for https")

    calculate = subparsers.add_parser('calculate', help='calculate result')
    calculate.add_argument(
        '--params', required=True, metavar='path', dest='params_path',
        action=util.EnvPathArgParseAction,
        help="calculate parameters file path "
             "(specified by opcut://params.yaml#)")
    calculate.add_argument(
        '--method', dest='method',
        default=common.Method.FORWARD_GREEDY,
        choices=[method.name for method in common.Method],
        action=_MethodParseAction,
        help="calculate method (default FORWARD_GREEDY)")
    calculate.add_argument(
        '--output', default=None, metavar='path', dest='output_path',
        action=util.EnvPathArgParseAction,
        help="optional output file path")

    output = subparsers.add_parser('output', help='generate output')
    output.add_argument(
        '--output', required=True, metavar='path', dest='output_path',
        action=util.EnvPathArgParseAction,
        help="output file path")

    for p in [calculate, output]:
        p.add_argument(
            '--result', required=True, metavar='path', dest='result_path',
            action=util.EnvPathArgParseAction,
            help="calculate result file path "
                 "(specified by opcut://result.yaml#)")
        p.add_argument(
            '--output-type', dest='output_type', default='PDF',
            choices=[output_type.name for output_type in common.OutputType],
            help="output type (default PDF)")
        p.add_argument(
            '--output-panel', default=None, metavar='panel_id',
            dest='output_panel_id', help="output panel id")

    dev_args = parser.add_argument_group('development arguments')
    dev_args.add_argument(
        '--json-schemas-path', metavar='path', dest='schemas_json_path',
        default=default_schemas_json_path,
        action=util.EnvPathArgParseAction,
        help="override json schemas directory path")
    dev_args.add_argument(
        '--ui-path', metavar='path', dest='ui_path',
        default=default_ui_path,
        action=util.EnvPathArgParseAction,
        help="override web ui directory path")

    return parser


class _MethodParseAction(argparse.Action):

    def __call__(self, parser, namespace, values, option_string=None):
        ret = []
        for value in (values if self.nargs else [values]):
            try:
                ret.append(common.Method[value])
            except Exception as e:
                parser.error(str(e))
        setattr(namespace, self.dest, ret if self.nargs else ret[0])


if __name__ == '__main__':
    sys.exit(main())
