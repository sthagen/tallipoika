import binascii
import pathlib
import struct

import tallipoika.py2es6 as py2es6

COMMA = ','
INVALID_NUMBER = 'null'
UPSTREAM_REF_TEST_DATA = pathlib.Path('test') / 'fixtures' / 'es6testfile100m.txt'


def verify(ieee_hex, expected) -> None:
    """Test program using a 100 million value file formatted as follows:
    value in ieee hex representation (1-16 digits) + ',' + correct ES6 format + '\n'
    """
    while len(ieee_hex) < 16:
        ieee_hex = '0' + ieee_hex
    value = struct.unpack('>d', binascii.a2b_hex(ieee_hex))[0]
    try:
        serialized = py2es6.serialize(value)
    except ValueError:
        if expected == INVALID_NUMBER:
            return
    if serialized == expected and value == float(serialized) and repr(value) == str(value):
        return
    raise ValueError('IEEE:   ' + ieee_hex + '\nPython: ' + serialized + '\nExpected: ' + expected)


def test_corners():
    assert verify('4340000000000001', '9007199254740994') is None
    assert verify('4340000000000002', '9007199254740996') is None
    assert verify('444b1ae4d6e2ef50', '1e+21') is None
    assert verify('3eb0c6f7a0b5ed8d', '0.000001') is None
    assert verify('3eb0c6f7a0b5ed8c', '9.999999999999997e-7') is None
    assert verify('8000000000000000', '0') is None
    assert verify('7fffffffffffffff', INVALID_NUMBER) is None
    assert verify('7ff0000000000000', INVALID_NUMBER) is None
    assert verify('fff0000000000000', INVALID_NUMBER) is None


def test_reference():
    with open(UPSTREAM_REF_TEST_DATA, 'r') as line_source:
        for count, line in enumerate(line_source):
            if line:
                i = line.find(COMMA)
                if i <= 0 or i >= len(line) - 1:
                    raise ValueError(f'bad line ({line}) at {count}')
                assert verify(line[:i], line[i + 1 : len(line) - 1]) is None
