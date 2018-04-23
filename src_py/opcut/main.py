import sys
import argparse
import yaml
import logging.config
import urllib.parse
import asyncio
import os.path

from opcut import util
from opcut import common
import opcut.json_validator
import opcut.csp
import opcut.server
import opcut.output


def main():
    """Application main entry point"""

    args = _create_parser().parse_args()

    if args.log_conf_path:
        with open(args.log_conf_path, encoding='utf-8') as log_conf_file:
            log_conf = yaml.safe_load(log_conf_file)
        opcut.json_validator.validate(log_conf, 'opcut://logging.yaml#')
        logging.config.dictConfig(log_conf)

    action_fn = {
        'server': server,
        'calculate': calculate,
        'output': output}.get(args.action, server)
    action_fn(args)


def server(args):
    """Server main entry point

    Args:
        args: command line argument

    """
    if sys.platform == 'win32':
        asyncio.set_event_loop(asyncio.ProactorEventLoop())

    addr = urllib.parse.urlparse(args.ui_addr)
    pem_path = args.ui_pem_path
    ui_path = args.ui_path or os.path.join(os.path.dirname(__file__), 'web')

    util.run_until_complete_without_interrupt(
        opcut.server.run(addr, pem_path, ui_path))


def calculate(args):
    """Calculate result and generate outputs

    Args:
        args: command line argument

    """
    with open(args.params_path, 'r', encoding='utf-8') as f:
        params_json_data = yaml.safe_load(f)
    opcut.json_validator.validate(params_json_data, 'opcut://params.yaml#')
    params = common.json_data_to_params(params_json_data)
    result = opcut.csp.calculate(params, args.method)
    result_json_data = common.result_to_json_data(result)
    with open(args.result_path, 'w', encoding='utf-8') as f:
        yaml.safe_dump(result_json_data, f,
                       indent=4, default_flow_style=False,
                       explicit_start=True, explicit_end=True)
    output(args)


def output(args):
    """Generate outputs based on calculation result

    Args:
        args: command line argument

    """
    if not args.output_path:
        return
    with open(args.result_path, 'r', encoding='utf-8') as f:
        result_json_data = yaml.safe_load(f)
    opcut.json_validator.validate(result_json_data, 'opcut://result.yaml#')
    result = common.json_data_to_result(result_json_data)
    output_type = common.OutputType[args.output_type]
    output_bytes = opcut.output.generate_output(result, output_type,
                                                args.output_panel_id)
    with open(args.output_path, 'wb') as f:
        f.write(output_bytes)


def _create_parser():
    parser = argparse.ArgumentParser(prog='opcut')
    parser.add_argument(
        '--log', default=None, metavar='path', dest='log_conf_path',
        help="logging configuration")
    subparsers = parser.add_subparsers(title='actions', dest='action')

    server = subparsers.add_parser('server', help='run web server')
    server.add_argument(
        '--ui-addr', default='http://0.0.0.0:8080',
        metavar='addr', dest='ui_addr',
        help="address of listening web ui socket formated as "
             "'<type>://<host>:<port>' - <type> is 'http' or 'https'; "
             "<host> is hostname; <port> is tcp port number "
             "(default http://0.0.0.0:8080)")
    server.add_argument(
        '--ui-pem', default=None, metavar='path', dest='ui_pem_path',
        help="web front-end pem file path - required for https")
    server.add_argument(
        '--ui-path', default=None, metavar='path', dest='ui_path',
        help="override  path to front-end web app directory")

    calculate = subparsers.add_parser('calculate', help='calculate result')
    calculate.add_argument(
        '--params', required=True, metavar='path', dest='params_path',
        help="calculate parameters file path "
             "(specified by opcut://params.yaml#)")
    calculate.add_argument(
        '--method', dest='method', type=common.Method,
        default=common.Method.FORWARD_GREEDY,
        choices=list(map(lambda x: x.name, common.Method)),
        help="calculate method (default FORWARD_GREEDY)")

    output = subparsers.add_parser('output', help='generate output')

    for p in [calculate, output]:
        p.add_argument(
            '--result', required=True, metavar='path', dest='result_path',
            help="calculate result file path "
                 "(specified by opcut://result.yaml#)")
        p.add_argument(
            '--output-type', dest='output_type', default='PDF',
            choices=list(map(lambda x: x.name, common.OutputType)),
            help="output type (default PDF)")
        p.add_argument(
            '--output-panel', default=None, metavar='panel_id',
            dest='output_panel_id', help="output panel id")
        p.add_argument(
            '--output', default=None, metavar='path', dest='output_path',
            help="optional output file path")

    return parser


if __name__ == '__main__':
    sys.exit(main())
