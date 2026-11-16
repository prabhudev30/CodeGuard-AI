
from codeguard.ruff_checker import check_code_quality


def test_clean_python(tmp_path):
    file = tmp_path / "clean.py"
    file.write_text("print('Hello')\n", encoding="utf-8")

    result = check_code_quality(file)

    assert result["status"] == "passed"
    assert result["issues"] == []


def test_unused_import(tmp_path):
    file = tmp_path / "unused.py"
    file.write_text("import os\n", encoding="utf-8")

    result = check_code_quality(file)

    assert result["status"] == "issues_found"
    assert any(
        issue["code"] == "F401"
        for issue in result["issues"]
    )


def test_undefined_variable(tmp_path):
    file = tmp_path / "undefined.py"
    file.write_text(
        "print(missing_variable)\n",
        encoding="utf-8",
    )

    result = check_code_quality(file)

    assert result["status"] == "issues_found"
    assert any(
        issue["code"] == "F821"
        for issue in result["issues"]
    )


def test_missing_file(tmp_path):
    file = tmp_path / "missing.py"

    result = check_code_quality(file)

    assert result["status"] == "error"
    assert result["issues"] == []


def test_multiple_issues(tmp_path):
    file = tmp_path / "multiple.py"
    file.write_text(
        "import os\nprint(missing_variable)\n",
        encoding="utf-8",
    )

    result = check_code_quality(file)

    codes = {issue["code"] for issue in result["issues"]}

    assert result["status"] == "issues_found"
    assert "F401" in codes
    assert "F821" in codes
