
from codeguard.reviewer import review_file


def test_clean_file(tmp_path):
    file = tmp_path / "clean.py"
    file.write_text("print('Hello')\n", encoding="utf-8")

    result = review_file(file)

    assert result["status"] == "passed"
    assert result["total_issues"] == 0
    assert result["syntax"]["status"] == "passed"
    assert result["quality"]["status"] == "passed"
    assert result["security"]["status"] == "passed"


def test_quality_issue(tmp_path):
    file = tmp_path / "quality.py"
    file.write_text("import os\n", encoding="utf-8")

    result = review_file(file)

    assert result["status"] == "issues_found"
    assert result["total_issues"] >= 1
    assert result["quality"]["status"] == "issues_found"


def test_security_issue(tmp_path):
    file = tmp_path / "security.py"
    file.write_text(
        "import subprocess\n"
        "subprocess.run('echo hello', shell=True)\n",
        encoding="utf-8",
    )

    result = review_file(file)

    assert result["status"] == "issues_found"
    assert result["security"]["status"] == "issues_found"
    assert result["total_issues"] >= 1


def test_invalid_syntax(tmp_path):
    file = tmp_path / "invalid.py"
    file.write_text(
        "def greet()\n    pass\n",
        encoding="utf-8",
    )

    result = review_file(file)

    assert result["status"] == "issues_found"
    assert result["syntax"]["status"] == "failed"
    assert result["total_issues"] >= 1


def test_missing_file(tmp_path):
    file = tmp_path / "missing.py"

    result = review_file(file)

    assert result["status"] == "error"
    assert result["message"] == "File does not exist"
