
from codeguard.security_checker import check_security


def test_safe_python(tmp_path):
    file = tmp_path / "safe.py"
    file.write_text("print('Hello')\n", encoding="utf-8")

    result = check_security(file)

    assert result["status"] == "passed"
    assert result["issues"] == []


def test_shell_true_detection(tmp_path):
    file = tmp_path / "shell.py"
    file.write_text(
        "import subprocess\n"
        "subprocess.run('echo hello', shell=True)\n",
        encoding="utf-8",
    )

    result = check_security(file)

    codes = {issue["test_id"] for issue in result["issues"]}

    assert result["status"] == "issues_found"
    assert "B602" in codes


def test_hardcoded_password(tmp_path):
    file = tmp_path / "password.py"
    file.write_text(
        "password = 'super_secret_password_123'\n",
        encoding="utf-8",
    )

    result = check_security(file)

    codes = {issue["test_id"] for issue in result["issues"]}

    assert result["status"] == "issues_found"
    assert "B105" in codes


def test_missing_file(tmp_path):
    file = tmp_path / "missing.py"

    result = check_security(file)

    assert result["status"] == "error"
    assert result["issues"] == []


def test_empty_file(tmp_path):
    file = tmp_path / "empty.py"
    file.write_text("", encoding="utf-8")

    result = check_security(file)

    assert result["status"] == "passed"
    assert result["issues"] == []
