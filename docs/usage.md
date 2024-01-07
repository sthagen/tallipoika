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

### Large Files and Comparing IO Mechanisms

Given the approx 25 Megabytes large JSON test file at <https://github.com/json-iterator/test-data/raw/master/large-file.json> 
at revision `sha1:0bce379832b475a6c21726ce37f971f8d849513b` from 2016-12-02 03:21:00 UTC with fingerprints:

- artifact:json-iterator_test-data_sha1-0bce3798_large-file.json:
  + blake2:f306519f67ddf66792eb6bbbcb48acedc7aedd2c9436c92877ecfa2bf36a7d1eaf0ef8895e0adaec54f532182c7a7b0dc8e057d485387ca1b00ba09bb8b79550
  + blake3:529335c194bceb86f853b7ad2db103fcb63fd0d9d9501e8b8610ea043cb9485c
  + bytes:26141343
  + crc32:c4a131b8
  + entropy:5.195488 per byte that is (64.9436 %)
  + file:(Unicode text, UTF-8 text, with very long lines (15435))
  + hex32:5b7b226964223a2232343839363531303435222c2274797065223a2243726561
  + md5:67a1a08c5d0638f0af254d6c0243696d
  + mime-encoding:(utf-8)
  + mime-type:(text/plain)
  + sha:6c5c3f760bb64426760682166e6df9218fe81b0f
  + sha256:4fc1e52c4e609febd05d75a24c84bc6957fa4d2cfb0d5fbebbac650bdc7ed8c0
  + sha384:e1b420c6b145f31a41a19b7f6365f8c25b337858c6d41c4132ef00deb3e3248e209e8b6c30e1fa7e072706927f393272
  + sha512:47bc1b24ffc67c0ebf3625ccd9bf73af2f08956b550e3bf1699c64b8e5685d50f8569ea560bdc050e3b980476f220e262c264e4baabadae57988ee72e526f4a9
  + ssdeep:49152:pjktmgtlFHs0ImDlf/2jhj1a7EksjuyOVQLHa7Ew4MePnj1hEyJWQCQzQQQQQ0kB:w
  + tlsh:T12F47D0E342884496CF433EC0988DB7C892ABA05BDFC4EC49D7B5DC19C9585FB12CE65A

As stated below the throughput is around 30361606 incoming bytes per second (around 29 Megabytes/second).

The JCS "compression" in the canonicalization case for that input file is around (resulting jcs.json has a size of 26129992 bytes): 1.0004, so nearly no compression.
But, the entropy has been reduced from down to 5.192266 i.e. from 64.9436 % down to 64.903325 % (the change is smaller than 0.05 % of 100 % or 0.06 % of the incoming entropy). 
Comparing canonicalization with serialization surprisingly finds:

```console
% hyperfine --warmup 3 \
  'tallipoika json-iterator_test-data_sha1-0bce3798_large-file.json -s -o json-iterator_test-data_sha1-0bce3798_large-file.serialized.json' \
  'tallipoika json-iterator_test-data_sha1-0bce3798_large-file.json -o json-iterator_test-data_sha1-0bce3798_large-file.jcs.json'
Benchmark 1: tallipoika json-iterator_test-data_sha1-0bce3798_large-file.json -s -o json-iterator_test-data_sha1-0bce3798_large-file.serialized.json
  Time (mean ± σ):      1.076 s ±  0.014 s    [User: 0.935 s, System: 0.060 s]
  Range (min … max):    1.062 s …  1.100 s    10 runs

Benchmark 2: tallipoika json-iterator_test-data_sha1-0bce3798_large-file.json -o json-iterator_test-data_sha1-0bce3798_large-file.jcs.json
  Time (mean ± σ):     861.3 ms ±   1.9 ms    [User: 733.6 ms, System: 57.6 ms]
  Range (min … max):   859.3 ms … 865.2 ms    10 runs

Summary
  tallipoika json-iterator_test-data_sha1-0bce3798_large-file.json -o json-iterator_test-data_sha1-0bce3798_large-file.jcs.json ran
    1.25 ± 0.02 times faster than tallipoika json-iterator_test-data_sha1-0bce3798_large-file.json -s \
                                    -o json-iterator_test-data_sha1-0bce3798_large-file.serialized.json
```

Comparing the above timings with the following (using stdin and stdout IO mechanisms instead of file paths) yields no surprises though:

```console
% hyperfine --warmup 3 \
  'tallipoika < json-iterator_test-data_sha1-0bce3798_large-file.json -s > json-iterator_test-data_sha1-0bce3798_large-file.serialized.json' \
  'tallipoika < json-iterator_test-data_sha1-0bce3798_large-file.json > json-iterator_test-data_sha1-0bce3798_large-file.jcs.json'
Benchmark 1: tallipoika < json-iterator_test-data_sha1-0bce3798_large-file.json -s > json-iterator_test-data_sha1-0bce3798_large-file.serialized.json
  Time (mean ± σ):      1.069 s ±  0.002 s    [User: 0.938 s, System: 0.060 s]
  Range (min … max):    1.066 s …  1.075 s    10 runs

Benchmark 2: tallipoika < json-iterator_test-data_sha1-0bce3798_large-file.json > json-iterator_test-data_sha1-0bce3798_large-file.jcs.json
  Time (mean ± σ):     866.9 ms ±   4.8 ms    [User: 736.5 ms, System: 58.7 ms]
  Range (min … max):   862.9 ms … 877.9 ms    10 runs

Summary
  tallipoika < json-iterator_test-data_sha1-0bce3798_large-file.json > json-iterator_test-data_sha1-0bce3798_large-file.jcs.json ran
    1.23 ± 0.01 times faster than tallipoika < json-iterator_test-data_sha1-0bce3798_large-file.json -s \
                                    > json-iterator_test-data_sha1-0bce3798_large-file.serialized.json
```
