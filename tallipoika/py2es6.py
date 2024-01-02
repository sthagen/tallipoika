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

    - (builtin) numbers are for now int and float but may be extended to other types
      that can be mapped to JSON numbers
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
    exponent = ''
    exponent_number = 0
    if (fndx := magnitude.find('e')) > 0:
        mantissa, exponent = magnitude[0:fndx], magnitude[fndx:]
        if exponent[2:3] == '0':  # Suppress leading zero on exponents
            exponent = exponent[:2] + exponent[3:]
        exponent_number = int(exponent[1:])

    integral = mantissa
    decimal_point = ''
    fractional = ''
    if (fndx := mantissa.find(DECIMAL_POINT)) > 0:
        decimal_point = DECIMAL_POINT
        integral, fractional = mantissa[:fndx], mantissa[fndx + 1 :]

    if fractional == DIGIT_ZERO:  # x.0 -> x
        decimal_point = ''
        fractional = ''

    if MIN_INTEGER_DIGITS < exponent_number < MAX_INTEGER_DIGITS:
        integral += fractional
        fractional = ''
        decimal_point = ''
        exponent = ''
        n = exponent_number - len(integral)
        while n >= 0:
            n -= 1
            integral += DIGIT_ZERO
    elif REPR_SWITCH_ABOVE < exponent_number < 0:
        fractional = integral + fractional
        integral = DIGIT_ZERO
        decimal_point = DECIMAL_POINT
        exponent = ''
        n = exponent_number
        while n < -1:
            n += 1
            fractional = DIGIT_ZERO + fractional

    return f'{sign}{integral}{decimal_point}{fractional}{exponent}'
