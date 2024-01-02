# Test Fixtures

The reference upstream test fixtures are from <https://github.com/cyberphone/json-canonicalization/tree/master/testdata>
the input and output folders.

The reference test data for the number conversion part is the 100 million lines test file from
<https://github.com/cyberphone/json-canonicalization/releases/download/es6testfile/es6testfile100m.txt.gz>

The taxonomy describing the unpacked es6testfile100m.txt file is 4036326174 bytes, 100_000_000 lines, and
a sha256 of `0f7dda6b0837dde083c5d6b896f7d62340c8a2415b0c7121d83145e08a755272`.

The upstream commit is `dc406ceaf94b5fa554fcabb92c091089c2357e83` where this data was taken from.

The initial implementation of `tallipoika` passes all tests.

The numerical test takes about 500 seconds on some development machine (excluding the download, unpacking, and verification
of the big test data file. 
