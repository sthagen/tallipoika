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

## Cursory Benchmarks

### References

Using small JSON files from the reference tests (approximately doubling the byte size every time) on a random 
developer machine and writing to the /dev/null sink:

```console
% hyperfine --warmup 3 \
  'tallipoika < test/fixtures/reference_upstream_input/unicode.json > /dev/null' \
  'tallipoika < test/fixtures/reference_upstream_input/arrays.json > /dev/null' \
  'tallipoika < test/fixtures/reference_upstream_input/structures.json > /dev/null' \
  'tallipoika < test/fixtures/reference_upstream_input/weird.json > /dev/null'
Benchmark 1: tallipoika < test/fixtures/reference_upstream_input/unicode.json > /dev/null
  Time (mean ± σ):     101.1 ms ±   0.4 ms    [User: 28.4 ms, System: 12.0 ms]
  Range (min … max):    99.8 ms … 102.0 ms    28 runs

Benchmark 2: tallipoika < test/fixtures/reference_upstream_input/arrays.json > /dev/null
  Time (mean ± σ):     101.2 ms ±   0.6 ms    [User: 28.5 ms, System: 12.1 ms]
  Range (min … max):   100.2 ms … 102.8 ms    28 runs

Benchmark 3: tallipoika < test/fixtures/reference_upstream_input/structures.json > /dev/null
  Time (mean ± σ):     101.1 ms ±   0.6 ms    [User: 28.5 ms, System: 12.1 ms]
  Range (min … max):    99.8 ms … 102.8 ms    28 runs

Benchmark 4: tallipoika < test/fixtures/reference_upstream_input/weird.json > /dev/null
  Time (mean ± σ):     101.3 ms ±   0.5 ms    [User: 28.4 ms, System: 12.1 ms]
  Range (min … max):   100.2 ms … 102.4 ms    28 runs

Summary
  tallipoika < test/fixtures/reference_upstream_input/unicode.json > /dev/null ran
    1.00 ± 0.01 times faster than tallipoika < test/fixtures/reference_upstream_input/structures.json > /dev/null
    1.00 ± 0.01 times faster than tallipoika < test/fixtures/reference_upstream_input/arrays.json > /dev/null
    1.00 ± 0.01 times faster than tallipoika < test/fixtures/reference_upstream_input/weird.json > /dev/null
```

Broad size progression info (39 to 62 to 138 to 283 chars):

```console
% wc test/fixtures/reference_upstream_input/{unicode,arrays,structures,weird}.json
       3       4      39 test/fixtures/reference_upstream_input/unicode.json
       8      12      62 test/fixtures/reference_upstream_input/arrays.json
       7      27     138 test/fixtures/reference_upstream_input/structures.json
      11      32     283 test/fixtures/reference_upstream_input/weird.json
      29      75     522 total
```


### Canonicalization of the CSAF v2.0 JSON Schema

```console
% hyperfine --warmup 3 'tallipoika < csaf_2_0.json > csaf_2_0.jcs.json'
Benchmark 1: tallipoika < csaf_2_0.json > csaf_2_0.jcs.json
  Time (mean ± σ):     103.8 ms ±   0.8 ms    [User: 29.8 ms, System: 12.5 ms]
  Range (min … max):   101.8 ms … 105.1 ms    28 runs

% wc csaf_2_0.json
    1343    4565   54123 csaf_2_0.json
% wc csaf_2_0.jcs.json
       0    2371   33804 csaf_2_0.jcs.json
```
