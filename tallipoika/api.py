"""JSON Canonicalization Scheme (JCS) serializer API."""
import math
from typing import Any, no_type_check

from tallipoika._factory import make_iterencode as _make_iterencode
from tallipoika.speedup import accelerated_make_encoder, encode_basestring, encode_basestring_ascii

COLON = ':'
COMMA = ','
SPACE = ' '

INFINITY = float('inf')
REPR_NAN = 'NaN'
REPR_POS_INF = 'Infinity'
REPR_NEG_INF = '-Infinity'


@no_type_check
class JSONEncoder:
    """JSON encoder for typical Python data structures.

    Encodes the following nine Python types as the following 7 JSON types:

    - Python `dict` -> JSON object
    - Python `list` and `tuple` -> JSON array
    - Python `str` -> JSON string
    - Python `float` and `int` -> JSON number
    - Python `True` ->JSON true
    - Python `False` -> JSON false
    - Python `None` -> JSON null

    To extend recognition to other objects, subclass and implement a `default` method that returns a serializable
    object for `obj` if possible, otherwise it should call the superclass implementation (to raise `TypeError`).
    """

    item_separator = f'{COMMA}{SPACE}'
    key_separator = f'{COLON}{SPACE}'

    @no_type_check
    def __init__(
        self,
        *,
        skipkeys=False,
        ensure_ascii=False,
        check_circular=True,
        allow_nan=True,
        sort_keys=True,
        indent=None,
        separators=(COMMA, COLON),
        default=None,
    ):
        """Constructor for JSONEncoder, with sensible defaults for JCS.

        All parameter defaults except the value for `sort_keys` are as per the standard Python implementation;
        for documentation cf. https://docs.python.org/3/library/json.html#json.JSONEncoder.

        The default value for the `sort_keys` parameter is `True`, so the output of dictionaries will be sorted by key.
        """
        self.skipkeys = skipkeys
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
    def default(self, obj):
        """Implement this method in a subclass such that it returns a serializable object for obj.

        For an example, cf. https://docs.python.org/3/library/json.html#json.JSONEncoder.default
        """
        raise TypeError(f"Object of type '{obj.__class__.__name__}' is not JSON serializable")

    @no_type_check
    def encode(self, obj):
        """Return a JSON string representation of a Python data structure."""
        if isinstance(obj, str):  # This is for extremely simple cases and benchmarks.
            return encode_basestring_ascii(obj) if self.ensure_ascii else encode_basestring(obj)
        # This doesn't pass the iterator directly to ''.join() because the exceptions aren't as detailed.
        # The list call should be roughly equivalent to the PySequence_Fast that ''.join() would do.
        chunks = self.iterencode(obj, _one_shot=False)
        if not isinstance(chunks, (list, tuple)):
            chunks = list(chunks)
        return ''.join(chunks)

    @no_type_check
    def iterencode(self, obj, _one_shot=False):
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
                return REPR_NAN
            if obj == _inf:
                return REPR_POS_INF
            if obj == _neginf:
                return REPR_NEG_INF

        if _one_shot and accelerated_make_encoder is not None and self.indent is None:
            return accelerated_make_encoder(
                markers,
                self.default,
                _encoder,
                self.indent,
                self.key_separator,
                self.item_separator,
                self.sort_keys,
                self.skipkeys,
                self.allow_nan,
            )(obj, 0)

        return _make_iterencode(
            markers,
            self.default,
            _encoder,
            self.indent,
            floatstr,
            self.key_separator,
            self.item_separator,
            self.sort_keys,
            self.skipkeys,
            _one_shot,
        )(obj, 0)


@no_type_check
def ensure_encoding(text: str, utf8: bool) -> str:
    return text.encode() if utf8 else text


@no_type_check
def canonicalize(obj, utf8=True):
    return ensure_encoding(JSONEncoder(sort_keys=True).encode(obj), utf8=utf8)


@no_type_check
def serialize(obj, utf8=True):
    return ensure_encoding(JSONEncoder(sort_keys=False).encode(obj), utf8=utf8)
