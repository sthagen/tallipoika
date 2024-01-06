import _io  # type: ignore
import pytest

import tallipoika.cli as cli
from tallipoika import VERSION


def test_parse_request_empty(capsys):
    options = cli.parse_request([])
    assert options.serialize_only is False
    assert options.version_request is False
    assert isinstance(options.out_path, _io.TextIOWrapper)
    out, err = capsys.readouterr()
    assert not out
    assert not err


def test_parse_request_help(capsys):
    for option in ('-h', '--help'):
        with pytest.raises(SystemExit) as err:
            cli.parse_request([option])
        assert not err.value.code
        out, err = capsys.readouterr()
        assert 'Path to the file to transform. Optional (default: STDIN)' in out
        assert not err


def test_parse_request_non_existing_in_path(capsys):
    with pytest.raises(SystemExit) as err:
        cli.parse_request(['--in-path', 'this-path-is-missing'])
    assert err.value.code == 2
    out, err = capsys.readouterr()
    banner_start = 'usage: tallipoika [-h] [--in-path IN_PATH]'
    assert err.startswith(banner_start)
    assert 'tallipoika: error: requested source (this-path-is-missing) does not exist' in err
    assert not out


def test_parse_request_folder_as_in_path(capsys):
    with pytest.raises(SystemExit) as err:
        cli.parse_request(['-i', 'test'])
    assert err.value.code == 2
    out, err = capsys.readouterr()
    banner_start = 'usage: tallipoika [-h] [--in-path IN_PATH]'
    assert err.startswith(banner_start)
    assert 'tallipoika: error: requested source (test) is not a file' in err
    assert not out


def test_parse_request_non_existing_in_path_pos(capsys):
    with pytest.raises(SystemExit) as err:
        cli.parse_request(['this-path-is-missing'])
    assert err.value.code == 2
    out, err = capsys.readouterr()
    banner_start = 'usage: tallipoika [-h] [--in-path IN_PATH]'
    assert err.startswith(banner_start)
    assert 'tallipoika: error: requested source (this-path-is-missing) does not exist' in err
    assert not out


def test_parse_request_folder_as_in_path_pos(capsys):
    with pytest.raises(SystemExit) as err:
        cli.parse_request(['test'])
    assert err.value.code == 2
    out, err = capsys.readouterr()
    banner_start = 'usage: tallipoika [-h] [--in-path IN_PATH]'
    assert err.startswith(banner_start)
    assert 'tallipoika: error: requested source (test) is not a file' in err
    assert not out


def test_app_in_path_test_fixtures_array_result(capsys):
    code = cli.app(['--in-path', 'test/fixtures/reference_upstream_input/arrays.json'])
    assert code == 0
    out, err = capsys.readouterr()
    assert '[56,{"d":true,"10":null,"1":[]}]' in out
    assert not err


def test_app_in_path_test_fixtures_array_result_serialize_only(capsys):
    code = cli.app(['-s', '--in-path', 'test/fixtures/reference_upstream_input/arrays.json'])
    assert code == 0
    out, err = capsys.readouterr()
    assert '[56,{"1":[],"10":null,"d":true}]' in out
    assert not err


def test_app_version(capsys):
    for option in ('-V', '--version'):
        code = cli.app([option])
        assert code == 0
        out, err = capsys.readouterr()
        assert VERSION in out
        assert not err
