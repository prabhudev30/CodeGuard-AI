
from pathlib import Path

from codeguard.syntax_checker import check_syntax


def test_valid_python(tmp_path):
    file = tmp_path / "valid.py"
    file.write_text("print('Hello')\n", encoding="utf-8")

    result = check_syntax(file)

    assert result["status"] == "passed"


def test_invalid_python(tmp_path):
    file = tmp_path / "invalid.py"
    file.write_text("def greet()\n    pass\n", encoding="utf-8")

    result = check_syntax(file)

    assert result["status"] == "failed"
    assert result["line"] == 1
    assert "expected ':'" in result["message"]


def test_missing_file(tmp_path):
    file = tmp_path / "missing.py"

    result = check_syntax(file)

    assert result["status"] == "error"
    assert result["message"] == "File does not exist"


def test_empty_python_file(tmp_path):
    file = tmp_path / "empty.py"
    file.write_text("", encoding="utf-8")

    result = check_syntax(file)

    assert result["status"] == "passed"


def test_utf8_bom_file(tmp_path):
    file = tmp_path / "bom.py"
    file.write_bytes(b"\xef\xbb\xbfprint('Hello')\n")

    result = check_syntax(file)

    assert result["status"] == "passed"


def test_invalid_utf8_file(tmp_path):
    file = tmp_path / "bad_encoding.py"
    file.write_bytes(b"\xff\xfe\x00")

    result = check_syntax(file)

    assert result["status"] == "error"
    assert "Unable to read file" in result["message"]
