"""JSON Canonicalization Scheme (JCS) serializer  - command line interface."""
import argparse
import _io  # type: ignore
import json
import pathlib
import sys
from typing import Union, no_type_check

import tallipoika.api as api
from tallipoika import (
    APP_ALIAS,
    APP_NAME,
    ENCODING,
    VERSION,
)


@no_type_check
def parse_request(argv: list[str]) -> Union[int, argparse.Namespace]:
    """Implementation of command line API returning parsed request."""
    parser = argparse.ArgumentParser(
        prog=APP_ALIAS, description=APP_NAME, formatter_class=argparse.RawTextHelpFormatter
    )
    parser.add_argument(
        '--in-path',
        '-i',
        dest='in_path',
        default='',
        help='Path to the file to transform. Optional\n(default: positional path value)',
        required=False,
    )
    parser.add_argument(
        'in_path_pos', nargs='?', default=sys.stdin, help='Path to the file to transform. Optional (default: STDIN)'
    )
    parser.add_argument(
        '--out-path',
        '-o',
        dest='out_path',
        default=sys.stdout,
        help='output file path for transformed file (default: STDOUT)',
    )
    parser.add_argument(
        '--serialize-only',
        '-s',
        dest='serialize_only',
        default=False,
        action='store_true',
        help='serialize only i.e. do not sort keys (default: False)',
    )
    parser.add_argument(
        '--version',
        '-V',
        dest='version_request',
        default=False,
        action='store_true',
        help='show version of the app and exit',
        required=False,
    )

    options = parser.parse_args(argv)

    if options.version_request:
        print(f'{APP_NAME} version {VERSION}')
        return 0

    if not options.in_path:
        if options.in_path_pos:
            options.in_path = options.in_path_pos
        else:
            options.in_path = sys.stdin

    if options.in_path is not sys.stdin:
        in_path = pathlib.Path(options.in_path)
        if in_path.exists():
            if in_path.is_file():
                return options
            parser.error(f'requested source ({in_path}) is not a file')
        parser.error(f'requested source ({in_path}) does not exist')

    return options


def process(options: argparse.Namespace) -> int:
    """Visit the source and yield the requested transformed target."""
    if isinstance(options.in_path, _io.TextIOWrapper):
        loaded = options.in_path.read()
    else:
        in_path = pathlib.Path(options.in_path)
        with open(in_path, 'r', encoding=ENCODING) as source:
            loaded = source.read()

    transformed = api.canonicalize(json.loads(loaded)) if options.serialize_only else api.serialize(json.loads(loaded))

    if isinstance(options.out_path, _io.TextIOWrapper):
        options.out_path.write(transformed.decode())
    else:
        out_path = pathlib.Path(options.out_path)
        with open(out_path, 'wb') as target:
            target.write(transformed)

    return 0


def app(argv: Union[list[str], None] = None) -> int:
    """Delegate processing to functional module."""
    argv = sys.argv[1:] if argv is None else argv
    options = parse_request(argv)
    if isinstance(options, int):
        return 0
    return process(options)
