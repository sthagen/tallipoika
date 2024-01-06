"""Serialize a Python numerical value as an ECMAScript v6 or later string."""
import math
from typing import Union, no_type_check

DASH = '-'
DECIMAL_POINT = '.'
DIGIT_ZERO = '0'
MIN_INTEGER_DIGITS = 0
MAX_INTEGER_DIGITS = 21
REPR_SWITCH_ABOVE = -7


@no_type_check
def serialize(number: Union[float, int]) -> str:
    """Serialize a Python builtin number as an ECMAScript v6 or later string.

    Implementation Note(s):

    - (builtin) numbers are for now int and float but may be extended to other types that can be mapped to JSON numbers
    - separate into the components:
      + sign
      + integral part
      + decimal point
      + fractional part
      + exponent part
    - return the concatenation of the components (some components may be empty)
    """
    if not math.isfinite(number):
        raise ValueError(f'invalid number ({number})')

    as_float = float(number)
    if as_float == 0:
        return DIGIT_ZERO

    as_text = str(as_float)
    sign = DASH if as_text[0] == DASH else ''
    magnitude = as_text[1:] if sign else as_text
    mantissa = magnitude
    e_part, e_number = '', 0
    if (exp_ndx := magnitude.find('e')) > 0:
        mantissa, e_part = magnitude[0:exp_ndx], magnitude[exp_ndx:]
        if e_part[2:3] == '0':  # remove leading zero of exponent representation
            e_part = f'{e_part[:2]}{e_part[3:]}'
        e_number = int(e_part[1:])

    i_part, d_point, f_part = mantissa, '', ''
    if (dec_ndx := mantissa.find(DECIMAL_POINT)) > 0:
        d_point = DECIMAL_POINT
        i_part, f_part = mantissa[:dec_ndx], mantissa[dec_ndx + 1 :]

    if f_part == DIGIT_ZERO:
        d_point, f_part = '', ''

    if MIN_INTEGER_DIGITS < e_number < MAX_INTEGER_DIGITS:
        up_shifts = e_number - len(i_part) - len(f_part) + 1
        return f'{sign}{i_part}{f_part}{DIGIT_ZERO * up_shifts}'  # removed decimal point and exponential part

    if REPR_SWITCH_ABOVE < e_number < 0:
        down_shifts = -e_number - 1
        return f'{sign}{DIGIT_ZERO}{DECIMAL_POINT}{DIGIT_ZERO * down_shifts}{i_part}{f_part}'  # removed exponential part

    return f'{sign}{i_part}{d_point}{f_part}{e_part}'
