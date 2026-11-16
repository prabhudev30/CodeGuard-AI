
import subprocess

from codeguard.git_checker import get_changed_python_files


def run_git(folder, *args):
    return subprocess.run(
        ["git", "-C", str(folder), *args],
        capture_output=True,
        text=True,
        check=True,
    )


def create_repo(folder):
    run_git(folder, "init")
    run_git(folder, "config", "user.name", "CodeGuard Test")
    run_git(folder, "config", "user.email", "test@example.com")

    file = folder / "sample.py"
    file.write_text("print('Hello')\n", encoding="utf-8")

    run_git(folder, "add", "sample.py")
    run_git(folder, "commit", "-m", "Initial test commit")


def test_no_changes(tmp_path):
    create_repo(tmp_path)

    result = get_changed_python_files(tmp_path)

    assert result["status"] == "passed"
    assert result["files"] == []


def test_modified_python_file(tmp_path):
    create_repo(tmp_path)

    file = tmp_path / "sample.py"
    file.write_text("print('Changed')\n", encoding="utf-8")

    result = get_changed_python_files(tmp_path)

    assert result["status"] == "passed"
    assert "sample.py" in result["files"]


def test_non_python_file_ignored(tmp_path):
    create_repo(tmp_path)

    file = tmp_path / "notes.txt"
    file.write_text("Hello\n", encoding="utf-8")

    result = get_changed_python_files(tmp_path)

    assert result["status"] == "passed"
    assert result["files"] == []


def test_missing_directory(tmp_path):
    missing = tmp_path / "missing"

    result = get_changed_python_files(missing)

    assert result["status"] == "error"
    assert result["files"] == []


def test_not_git_repository(tmp_path):
    result = get_changed_python_files(tmp_path)

    assert result["status"] == "error"
    assert result["message"] == "Not a Git repository"


def test_untracked_python_file(tmp_path):
    create_repo(tmp_path)

    new_file = tmp_path / "new_feature.py"
    new_file.write_text("print('New feature')\n", encoding="utf-8")

    result = get_changed_python_files(tmp_path)

    assert result["status"] == "passed"
    assert "new_feature.py" in result["files"]


def test_untracked_python_file_in_subfolder(tmp_path):
    create_repo(tmp_path)

    folder = tmp_path / "features"
    folder.mkdir()

    new_file = folder / "new_feature.py"
    new_file.write_text("print('Nested')\n", encoding="utf-8")

    result = get_changed_python_files(tmp_path)

    assert result["status"] == "passed"
    assert "features/new_feature.py" in result["files"]


def test_staged_new_python_file(tmp_path):
    create_repo(tmp_path)

    new_file = tmp_path / "staged.py"
    new_file.write_text("print('Staged')\n", encoding="utf-8")

    run_git(tmp_path, "add", "staged.py")

    result = get_changed_python_files(tmp_path)

    assert result["status"] == "passed"
    assert "staged.py" in result["files"]



def test_git_operation_timeout(tmp_path):
    from unittest.mock import patch
    with patch("codeguard.git_checker.subprocess.run", side_effect=subprocess.TimeoutExpired(cmd="git", timeout=15)):
        result = get_changed_python_files(tmp_path)
    assert result["status"] == "error"
    assert result["message"] == "Git operation timed out"
    assert result["files"] == []
