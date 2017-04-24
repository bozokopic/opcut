import sys
import argparse
import yaml
import logging.config
import urllib.parse
import aiohttp.web
import ssl
import asyncio
import contextlib

from opcut import util
import opcut.json_validator


def main():
    args = _create_parser().parse_args()

    if args.log_conf_path:
        with open(args.log_conf_path, encoding='utf-8') as log_conf_file:
            log_conf = yaml.safe_load(log_conf_file)
        opcut.json_validator.validate(log_conf, 'opcut://logging.yaml#')
        logging.config.dictConfig(log_conf)

    util.run_until_complete_without_interrupt(async_main(args))


async def async_main(args):

    addr = urllib.parse.urlparse(args.ui_addr)

    if addr.scheme == 'https':
        ssl_ctx = ssl.SSLContext(ssl.PROTOCOL_SSLv23)
        ssl_ctx.load_cert_chain(args.ui_pem_path)
    else:
        ssl_ctx = None

    app = aiohttp.web.Application()
    app.router.add_route('GET', '/',
                         lambda req: aiohttp.web.HTTPFound('/index.html'))
    app.router.add_static('/', args.ui_path)
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


def _create_parser():
    parser = argparse.ArgumentParser(prog='opcut')
    parser.add_argument(
        '--ui-addr', default='http://0.0.0.0:8080',
        metavar='addr', dest='ui_addr',
        help="address of listening web ui socket formated as "
             "'<type>://<host>:<port>' - <type> is 'http' or 'https'; "
             "<host> is hostname; <port> is tcp port number "
             "(default http://0.0.0.0:8080)")
    parser.add_argument(
        '--ui-path', default='web',
        metavar='path', dest='ui_path',
        help="web front-end path (default web)")
    parser.add_argument(
        '--ui-pem', default=None,
        metavar='path', dest='ui_pem_path',
        help="web front-end pem file path - required for https")
    parser.add_argument(
        '--log', default=None, metavar='path', dest='log_conf_path',
        help="logging configuration")
    return parser


if __name__ == '__main__':
    sys.exit(main())
