# Usage

Simple JCS library and command line application - probably not useful to many.

## Synopsis

```console
usage: tallipoika [-h] [--in-path IN_PATH] [--out-path OUT_PATH] [--serialize-only] [--version] [in_path_pos]

Stableson (Finnish: tallipoika) - a JSON Canonicalization Scheme (JCS) implementation.

positional arguments:
  in_path_pos           Path to the file to transform. Optional (default: STDIN)

options:
  -h, --help            show this help message and exit
  --in-path IN_PATH, -i IN_PATH
                        Path to the file to transform. Optional
                        (default: positional path value)
  --out-path OUT_PATH, -o OUT_PATH
                        output file path for transformed file (default: STDOUT)
  --serialize-only, -s  serialize only i.e. do not sort keys (default: False)
  --version, -V         show version of the app and exit
```

### Example

Canonicalization of reference example for arrays:

```console
% tallipoika < test/fixtures/reference_upstream_input/arrays.json
[56,{"d":true,"10":null,"1":[]}]
```

Serialization only:

```console
% tallipoika -s < test/fixtures/reference_upstream_input/arrays.json
[56,{"1":[],"10":null,"d":true}]
```

### Version

```console
% tallipoika -V
Stableson (Finnish: tallipoika) - a JSON Canonicalization Scheme (JCS) implementation. version 2024.1.6+parent.g6c33ae2f
```
