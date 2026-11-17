
import json
import subprocess
from unittest.mock import patch

import pytest

from codeguard.git_checker import get_changed_python_files
from codeguard.ruff_checker import check_code_quality
from codeguard.security_checker import check_security
from codeguard.tool_path import resolve_executable


def test_missing_executable():
    with patch("codeguard.tool_path.shutil.which", return_value=None):
        assert resolve_executable("git") is None


def test_git_missing_executable(tmp_path):
    with patch(
        "codeguard.git_checker.resolve_executable",
        return_value=None,
    ):
        result = get_changed_python_files(tmp_path)

    assert result["status"] == "error"
    assert result["message"] == "Git was not found"
    assert result["files"] == []


def test_ruff_missing_executable(tmp_path):
    path = tmp_path / "sample.py"
    path.write_text("print(1)\n", encoding="utf-8")

    with patch(
        "codeguard.ruff_checker.resolve_executable",
        return_value=None,
    ):
        result = check_code_quality(path)

    assert result["status"] == "error"
    assert result["message"] == "Ruff was not found"


@pytest.mark.parametrize(
    "output",
    ["not-json", "{}", "null"],
)
def test_ruff_invalid_output(tmp_path, output):
    path = tmp_path / "sample.py"
    path.write_text("print(1)\n", encoding="utf-8")

    completed = subprocess.CompletedProcess(
        args=["ruff"],
        returncode=0,
        stdout=output,
        stderr="",
    )

    with (
        patch(
            "codeguard.ruff_checker.resolve_executable",
            return_value=path,
        ),
        patch(
            "codeguard.ruff_checker.subprocess.run",
            return_value=completed,
        ),
    ):
        result = check_code_quality(path)

    assert result["status"] == "error"
    assert result["message"] == "Ruff returned invalid output"


@pytest.mark.parametrize(
    "output",
    ["not-json", "[]", '{"results": null}'],
)
def test_bandit_invalid_output(tmp_path, output):
    path = tmp_path / "sample.py"
    path.write_text("print(1)\n", encoding="utf-8")

    completed = subprocess.CompletedProcess(
        args=["python"],
        returncode=0,
        stdout=output,
        stderr="",
    )

    with (
        patch(
            "codeguard.security_checker.importlib.util.find_spec",
            return_value=object(),
        ),
        patch(
            "codeguard.security_checker.subprocess.run",
            return_value=completed,
        ),
    ):
        result = check_security(path)

    assert result["status"] == "error"
    assert result["message"] == "Bandit returned invalid output"


def test_ruff_uses_argument_separator(tmp_path):
    path = tmp_path / "sample.py"
    path.write_text("print(1)\n", encoding="utf-8")

    completed = subprocess.CompletedProcess(
        args=["ruff"],
        returncode=0,
        stdout=json.dumps([]),
        stderr="",
    )

    with patch(
        "codeguard.ruff_checker.resolve_executable",
        return_value=path,
    ), patch(
        "codeguard.ruff_checker.subprocess.run",
        return_value=completed,
    ) as mocked:
        check_code_quality(path)

    command = mocked.call_args.args[0]

    assert command[-2:] == ["--", str(path)]
    assert mocked.call_args.kwargs["stdin"] == subprocess.DEVNULL


def test_bandit_uses_argument_separator(tmp_path):
    path = tmp_path / "sample.py"
    path.write_text("print(1)\n", encoding="utf-8")

    completed = subprocess.CompletedProcess(
        args=["python"],
        returncode=0,
        stdout=json.dumps({"results": []}),
        stderr="",
    )

    with patch(
        "codeguard.security_checker.importlib.util.find_spec",
        return_value=object(),
    ), patch(
        "codeguard.security_checker.subprocess.run",
        return_value=completed,
    ) as mocked:
        check_security(path)

    command = mocked.call_args.args[0]

    assert command[-2:] == ["--", str(path)]
    assert mocked.call_args.kwargs["stdin"] == subprocess.DEVNULL
