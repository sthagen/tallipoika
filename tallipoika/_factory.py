"""Special factory for iterencode function covering some use cases in the tallipoika JSONEncoder."""
from typing import no_type_check

import tallipoika.py2es6 as py2es6

ENCODING_FOR_SORT = 'utf-16_be'
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
JSON_FNT_MAP = {None: JSON_NULL_REP, True: JSON_TRUE_REP, False: JSON_FALSE_REP}


@no_type_check
def make_iterencode(
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
    def _iterencode_list(seq, _current_indent_level: int):
        if not seq:
            yield EMPTY_ARRAY_REP
            return
        if markers is not None:
            marker_id = id(seq)
            if marker_id in markers:
                raise ValueError('circular reference detected for sequence')
            markers[marker_id] = seq
        buf = OPEN_SB
        if _indent is not None:
            _current_indent_level += 1
            newline_indent = f'{NL}{_indent * _current_indent_level}'
            separator = f'{_item_separator}{newline_indent}'
            buf += newline_indent
        else:
            newline_indent = None
            separator = _item_separator
        is_first = True
        for value in seq:
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
    def _iterencode_dict(assoc, _current_indent_level):
        if not assoc:
            yield EMPTY_OBJECT_REP
            return
        if markers is not None:
            marker_id = id(assoc)
            if marker_id in markers:
                raise ValueError('circular reference detected for dict')
            markers[marker_id] = assoc
        yield OPEN_CB
        if _indent is not None:
            _current_indent_level += 1
            newline_indent = f'{NL}{_indent * _current_indent_level}'
            item_separator = f'{_item_separator}{newline_indent}'
            yield newline_indent
        else:
            newline_indent = None
            item_separator = _item_separator
        is_first = True
        items = sorted(assoc.items(), key=lambda kv: kv[0].encode(ENCODING_FOR_SORT)) if _sort_keys else assoc.items()
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
            yield f'{NL}{_indent * _current_indent_level}'
        yield CLOSE_CB
        if markers is not None:
            try:
                marker_id  # noqa
            except NameError:
                pass
            else:
                del markers[marker_id]

    @no_type_check
    def _iterencode(obj, _current_indent_level):
        if isinstance(obj, str):
            yield _encoder(obj)
        elif any(obj is atom for atom in (False, None, True)):
            yield JSON_FNT_MAP[obj]
        elif isinstance(obj, (float, int)):
            # see comment for float/int in _make_iterencode
            yield py2es6.serialize(obj)
        elif isinstance(obj, (list, tuple)):
            yield from _iterencode_list(obj, _current_indent_level)
        elif isinstance(obj, dict):
            yield from _iterencode_dict(obj, _current_indent_level)
        else:
            if markers is not None:
                marker_id = id(obj)
                if marker_id in markers:
                    raise ValueError('circular reference detected')
                markers[marker_id] = obj
            obj = _default(obj)
            yield from _iterencode(obj, _current_indent_level)
            if markers is not None:
                try:
                    marker_id  # noqa
                except NameError:
                    pass
                else:
                    del markers[marker_id]

    return _iterencode
