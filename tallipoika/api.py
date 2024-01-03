"""JSON Canonicalization Scheme (JCS) serializer."""
import math
import re
from typing import Any, no_type_check

import tallipoika.py2es6 as py2es6

try:
    from _json import encode_basestring_ascii as c_encode_basestring_ascii
except ImportError:
    c_encode_basestring_ascii = None  # type: ignore
try:
    from _json import encode_basestring as c_encode_basestring  # type: ignore
except ImportError:
    c_encode_basestring = None
try:
    from _json import make_encoder as c_make_encoder
except ImportError:
    c_make_encoder = None  # type: ignore

COLON = ':'
COMMA = ','
SPACE = ' '
OPEN_SB = '['
CLOSE_SB = ']'
EMPTY_ARRAY_REP = f'{OPEN_SB}{CLOSE_SB}'
OPEN_CB = '{'
CLOSE_CB = '}'
EMPTY_OBJECT_REP = f'{OPEN_CB}{CLOSE_CB}'
NL = '\n'

JSON_FALSE_REP = 'false'
JSON_NULL_REP = 'null'
JSON_TRUE_REP = 'true'
JSON_FNT_MAP = {None: 'null', True: 'true', False: 'false'}

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

INFINITY = float('inf')


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
            else:
                # surrogate pair
                n -= 0x10000
                s1 = 0xD800 | ((n >> 10) & 0x3FF)
                s2 = 0xDC00 | (n & 0x3FF)
                return f'\\u{s1:04x}\\u{s2:04x}'

    return f'"{ESCAPE_ASCII.sub(replace, text)}"'


encode_basestring_ascii = c_encode_basestring_ascii or py_encode_basestring_ascii  # type: ignore


@no_type_check
class JSONEncoder(object):
    """JSON encoder for typical Python data structures.

    Encodes the following nine Python types as the following 7 JSON types:

    - Python `dict` -> JSON object
    - Python `list` and `tuple` -> JSON array
    - Python `str` -> JSON string
    - Python `float` and `int` -> JSON number
    - Python `True` ->JSON true
    - Python `False` -> JSON false
    - Python `None` -> JSON null

    To extend recognition to other objects, subclass and implement a `.default()` method that returns a serializable
    object for `o` if possible, otherwise it should call the superclass implementation (to raise `TypeError`).
    """

    item_separator = f'{COMMA}{SPACE}'
    key_separator = f'{COLON}{SPACE}'

    @no_type_check
    def __init__(
        self,
        *,
        skip_keys=False,
        ensure_ascii=False,
        check_circular=True,
        allow_nan=True,
        sort_keys=True,
        indent=None,
        separators=(COMMA, COLON),
        default=None,
    ):
        """Constructor for JSONEncoder, with sensible defaults.

        If skip_keys is false, then it is a TypeError to attempt encoding of keys that are not str, int, float or None.
        If skip_keys is True, such items are simply skipped.

        If ensure_ascii is true, the output is guaranteed to be str objects with all incoming non-ASCII characters
        escaped.  If ensure_ascii is false, the output can contain non-ASCII characters.

        If check_circular is true, then lists, dicts, and custom encoded objects will be checked for circular references
        during encoding to prevent an infinite recursion (which would cause an OverflowError). Otherwise, no such check
        takes place.

        If allow_nan is true, then NaN, Infinity, and -Infinity will be encoded as such.  This behavior is not JSON
        specification compliant, but is consistent with most JavaScript based encoders and decoders. Otherwise, it will
        be a ValueError to encode such floats.

        If sort_keys is true, then the output of dictionaries will be sorted by key; this is useful for regression tests
        to ensure that JSON serializations can be compared on a day-to-day basis.

        If indent is a non-negative integer, then JSON array elements and object members will be pretty-printed with
        that indent level.  An indent level of 0 will only insert newlines. None is the most compact representation.

        If specified, separators should be an (item_separator, key_separator) tuple.  The default is
        (', ', ': ') if *indent* is ``None`` and(',', ': ') otherwise.  To get the most compact JSON representation,
        you should specify (',', ':') to eliminate whitespace.

        If specified, default is a function that gets called for objects that can't otherwise be serialized.  It should
        return a JSON encodable version of the object or raise a ``TypeError``.

        """

        self.skip_keys = skip_keys
        self.ensure_ascii = ensure_ascii
        self.check_circular = check_circular
        self.allow_nan = allow_nan
        self.sort_keys = sort_keys
        self.indent = indent
        if separators is not None:
            self.item_separator, self.key_separator = separators
        elif indent is not None:
            self.item_separator = COMMA
        if default is not None:
            self.default = default

    @no_type_check
    def default(self, o):
        """Implement this method in a subclass such that it returns a serializable object for o.

        For example, to support arbitrary iterators, you could implement default like this::

            def default(self, o):
                try:
                    iterable = iter(o)
                except TypeError:
                    pass
                else:
                    return list(iterable)
                return JSONEncoder.default(self, o) # Let the base class default method raise the TypeError

        """
        raise TypeError(f"Object of type '{o.__class__.__name__}' is not JSON serializable")

    @no_type_check
    def encode(self, o):
        """Return a JSON string representation of a Python data structure.

        >>> from json.encoder import JSONEncoder
        >>> JSONEncoder().encode({"foo": ["bar", "baz"]})
        '{"foo": ["bar", "baz"]}'

        """
        if isinstance(o, str):  # This is for extremely simple cases and benchmarks.
            return encode_basestring_ascii(o) if self.ensure_ascii else encode_basestring(o)
        # This doesn't pass the iterator directly to ''.join() because the exceptions aren't as detailed.
        # The list call should be roughly equivalent to the PySequence_Fast that ''.join() would do.
        chunks = self.iterencode(o, _one_shot=False)
        if not isinstance(chunks, (list, tuple)):
            chunks = list(chunks)
        return ''.join(chunks)

    @no_type_check
    def iterencode(self, o, _one_shot=False):
        """Encode the given object and yield each string representation as available.

        For example:

            for chunk in JSONEncoder().iterencode(big_object):
                mysocket.write(chunk)

        """
        markers = {} if self.check_circular else None
        _encoder = encode_basestring_ascii if self.ensure_ascii else encode_basestring

        def floatstr(obj: Any, allow_nan=self.allow_nan, _repr=float.__repr__, _inf=INFINITY, _neginf=-INFINITY):
            """Check for specials.

            Note that this type of test is processor and platform-specific, so tests shall not rely on the internals.
            """
            if math.isfinite(obj):
                return _repr(obj)  # noqa
            elif not allow_nan:
                raise ValueError(f'out of range float value {repr(obj)} is not JSON compliant')

            if math.isnan(obj):
                return 'NaN'
            if obj == _inf:
                return 'Infinity'
            if obj == _neginf:
                return '-Infinity'

        if _one_shot and c_make_encoder is not None and self.indent is None:
            _iterencode = c_make_encoder(
                markers,
                self.default,
                _encoder,
                self.indent,
                self.key_separator,
                self.item_separator,
                self.sort_keys,
                self.skip_keys,
                self.allow_nan,
            )
        else:
            _iterencode = _make_iterencode(
                markers,
                self.default,
                _encoder,
                self.indent,
                floatstr,
                self.key_separator,
                self.item_separator,
                self.sort_keys,
                self.skip_keys,
                _one_shot,
            )
        return _iterencode(o, 0)


@no_type_check
def _make_iterencode(
    markers,
    _default,
    _encoder,
    _indent,
    _floatstr,
    _key_separator,
    _item_separator,
    _sort_keys,
    _skip_keys,
    _one_shot,
    # HACK: hand-optimized bytecode; turn globals into locals
    ValueError=ValueError,
    dict=dict,
    float=float,
    id=id,
    int=int,
    isinstance=isinstance,
    list=list,
    str=str,
    tuple=tuple,
    _intstr=int.__str__,
):
    if _indent is not None and not isinstance(_indent, str):
        _indent = SPACE * _indent

    @no_type_check
    def _iterencode_list(lst, _current_indent_level: int):
        if not lst:
            yield EMPTY_ARRAY_REP
            return
        if markers is not None:
            marker_id = id(lst)
            if marker_id in markers:
                raise ValueError('circular reference detected for sequence')
            markers[marker_id] = lst
        buf = OPEN_SB
        if _indent is not None:
            _current_indent_level += 1
            newline_indent = NL + _indent * _current_indent_level
            separator = _item_separator + newline_indent
            buf += newline_indent
        else:
            newline_indent = None
            separator = _item_separator
        is_first = True
        for value in lst:
            if is_first:
                is_first = False
            else:
                buf = separator
            if isinstance(value, str):
                yield buf + _encoder(value)
            elif any(value is atom for atom in (False, None, True)):
                yield buf + JSON_FNT_MAP[value]
            elif isinstance(value, (float, int)):
                # Subclasses of float and int may override __str__, but should still serialize as numbers in JSON.
                # One example within the standard library is IntEnum.
                yield buf + py2es6.serialize(value)
            else:
                yield buf
                chunker = (
                    _iterencode_list
                    if isinstance(value, (list, tuple))
                    else (_iterencode_dict if isinstance(value, dict) else _iterencode)
                )
                yield from chunker(value, _current_indent_level)
        if newline_indent is not None:
            _current_indent_level -= 1
            yield f'{NL}{_indent * _current_indent_level}'
        yield CLOSE_SB
        if markers is not None:
            try:
                marker_id  # noqa
            except NameError:
                pass
            else:
                del markers[marker_id]

    @no_type_check
    def _iterencode_dict(dct, _current_indent_level):
        if not dct:
            yield EMPTY_OBJECT_REP
            return
        if markers is not None:
            marker_id = id(dct)
            if marker_id in markers:
                raise ValueError('circular reference detected for dict')
            markers[marker_id] = dct
        yield OPEN_CB
        if _indent is not None:
            _current_indent_level += 1
            newline_indent = f'{NL}{_indent * _current_indent_level}'
            item_separator = _item_separator + newline_indent
            yield newline_indent
        else:
            newline_indent = None
            item_separator = _item_separator
        is_first = True
        items = sorted(dct.items(), key=lambda kv: kv[0].encode('utf-16_be')) if _sort_keys else dct.items()
        for key, value in items:
            if isinstance(key, str):
                pass
            # JavaScript is weakly typed for these, so it makes sense to also allow them.
            # Many encoders seem to do something like this.
            elif isinstance(key, (float, int)):
                # see comment for float/int in _make_iterencode
                key = py2es6.serialize(key)
            elif any(value is atom for atom in (False, None, True)):
                key = JSON_FNT_MAP[value]
            elif _skip_keys:
                continue
            else:
                raise TypeError(f'key {repr(key)} is not a string')
            if is_first:
                is_first = False
            else:
                yield item_separator

            yield _encoder(key)
            yield _key_separator

            if isinstance(value, str):
                yield _encoder(value)
            elif any(value is atom for atom in (False, None, True)):
                yield JSON_FNT_MAP[value]
            elif isinstance(value, (float, int)):
                # see comment for int/float in _make_iterencode
                yield py2es6.serialize(value)
            else:
                chunker = (
                    _iterencode_list
                    if isinstance(value, (list, tuple))
                    else (_iterencode_dict if isinstance(value, dict) else _iterencode)
                )
                yield from chunker(value, _current_indent_level)
        if newline_indent is not None:
            _current_indent_level -= 1
            yield NL + _indent * _current_indent_level
        yield CLOSE_CB
        if markers is not None:
            try:
                marker_id  # noqa
            except NameError:
                pass
            else:
                del markers[marker_id]

    @no_type_check
    def _iterencode(o, _current_indent_level):
        if isinstance(o, str):
            yield _encoder(o)
        elif any(o is atom for atom in (False, None, True)):
            yield JSON_FNT_MAP[o]
        elif isinstance(o, (float, int)):
            # see comment for float/int in _make_iterencode
            yield py2es6.serialize(o)
        elif isinstance(o, (list, tuple)):
            yield from _iterencode_list(o, _current_indent_level)
        elif isinstance(o, dict):
            yield from _iterencode_dict(o, _current_indent_level)
        else:
            if markers is not None:
                marker_id = id(o)
                if marker_id in markers:
                    raise ValueError('circular reference detected')
                markers[marker_id] = o
            o = _default(o)
            yield from _iterencode(o, _current_indent_level)
            if markers is not None:
                try:
                    marker_id  # noqa
                except NameError:
                    pass
                else:
                    del markers[marker_id]

    return _iterencode


@no_type_check
def ensure_encoding(text: str, utf8: bool) -> str:
    return text.encode() if utf8 else text


@no_type_check
def canonicalize(obj, utf8=True):
    return ensure_encoding(JSONEncoder(sort_keys=True).encode(obj), utf8=utf8)


@no_type_check
def serialize(obj, utf8=True):
    return ensure_encoding(JSONEncoder(sort_keys=False).encode(obj), utf8=utf8)
