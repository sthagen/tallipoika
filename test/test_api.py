import json
import pathlib

from tallipoika.api import canonicalize

ENCODING = 'utf-8'
NL = '\n'
test_data_root: pathlib.Path = pathlib.Path('test') / 'fixtures'
input_data_root: pathlib.Path = test_data_root / 'reference_upstream_input'
output_data_root: pathlib.Path = test_data_root / 'reference_upstream_output'


def test_upstream():
    for case in sorted(input_data_root.glob('*.json')):
        file_name = case.name
        with open(output_data_root / file_name, 'r', encoding=ENCODING) as sink:
            expected = sink.read().encode()

        with open(input_data_root / file_name, 'r', encoding=ENCODING) as source:
            loaded = source.read()

        actual = canonicalize(json.loads(loaded))
        recycled = canonicalize(json.loads(actual.decode(ENCODING, 'strict')))

        assert actual == expected
        assert actual == recycled
