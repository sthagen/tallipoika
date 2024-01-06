"""JSON encoding dispatch that offers C implementations from standard Python install if available."""
import re
from typing import no_type_check

try:
    from _json import encode_basestring_ascii as c_encode_basestring_ascii
except ImportError:
    c_encode_basestring_ascii = None  # type: ignore
try:
    from _json import encode_basestring as c_encode_basestring  # type: ignore
except ImportError:
    c_encode_basestring = None
try:
    from _json import make_encoder as accelerated_make_encoder
except ImportError:
    accelerated_make_encoder = None  # type: ignore

ESCAPE = re.compile(r'[\x00-\x1f\\"\b\f\n\r\t]')
ESCAPE_ASCII = re.compile(r'([\\"]|[^\ -~])')
HAS_UTF8 = re.compile(b'[\x80-\xff]')
ESCAPE_DCT = {
    '\\': '\\\\',
    '"': '\\"',
    '\b': '\\b',
    '\f': '\\f',
    '\n': '\\n',
    '\r': '\\r',
    '\t': '\\t',
}
for i in range(0x20):
    ESCAPE_DCT.setdefault(chr(i), '\\u{0:04x}'.format(i))


@no_type_check
def py_encode_basestring(text: str) -> str:
    """Return a JSON representation of a Python string."""

    def replace(match):
        return ESCAPE_DCT[match.group(0)]

    return f'"{ESCAPE.sub(replace, text)}"'


encode_basestring = c_encode_basestring or py_encode_basestring


@no_type_check
def py_encode_basestring_ascii(text: str) -> str:
    """Return an ASCII-only JSON representation of a Python string."""

    def replace(match):
        char = match.group(0)
        try:
            return ESCAPE_DCT[char]
        except KeyError:
            n = ord(char)
            if n < 0x10000:
                return '\\u{0:04x}'.format(n)
            else:  # surrogate pair
                n -= 0x10000
                s1 = 0xD800 | ((n >> 10) & 0x3FF)
                s2 = 0xDC00 | (n & 0x3FF)
                return f'\\u{s1:04x}\\u{s2:04x}'

    return f'"{ESCAPE_ASCII.sub(replace, text)}"'


encode_basestring_ascii = c_encode_basestring_ascii or py_encode_basestring_ascii  # type: ignore
