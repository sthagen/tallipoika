# API

## Python

Interactive example session:

```console
% python
Python 3.10.12 (main, Jul 16 2023, 10:40:08) [Clang 16.0.6 ] on darwin
Type "help", "copyright", "credits" or "license" for more information.
>>> import json
>>> import tallipoika.api as api
>>> api.canonicalize({'foo': 'bar', 'baz':    'quux'})
b'{"baz":"quux","foo":"bar"}'
>>> data = json.load(open('test/fixtures/reference_upstream_input/arrays.json', 'rb'))
>>> data
[56, {'d': True, '10': None, '1': []}]
>>> print(api.canonicalize(data))
b'[56,{"1":[],"10":null,"d":true}]'
>>> print(api.canonicalize(data).decode())
[56,{"1":[],"10":null,"d":true}]
>>> print(api.serialize(data).decode())
[56,{"d":true,"10":null,"1":[]}]
>>>
```
