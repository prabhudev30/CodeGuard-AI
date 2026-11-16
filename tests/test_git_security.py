import os
import subprocess
import pytest
from codeguard.git_checker import get_changed_python_files


def make_repo(path):
    path.mkdir()
    subprocess.run(["git", "init", "-q", str(path)], check=True)
    subprocess.run(["git", "-C", str(path), "config", "user.email", "test@example.com"], check=True)
    subprocess.run(["git", "-C", str(path), "config", "user.name", "Test User"], check=True)
    (path / "initial.txt").write_text("initial", encoding="utf-8")
    subprocess.run(["git", "-C", str(path), "add", "initial.txt"], check=True)
    subprocess.run(["git", "-C", str(path), "commit", "-qm", "initial"], check=True)


def test_filename_with_spaces(tmp_path):
    repo = tmp_path / "repo"
    make_repo(repo)
    (repo / "my test file.py").write_text("x = 1", encoding="utf-8")
    result = get_changed_python_files(repo)
    assert result["status"] == "passed"
    assert "my test file.py" in result["files"]


def test_external_symlink_is_not_scanned(tmp_path):
    repo = tmp_path / "repo"
    make_repo(repo)
    outside = tmp_path / "outside.py"
    outside.write_text("x = 1", encoding="utf-8")
    link = repo / "external.py"
    try:
        os.symlink(outside, link)
    except (OSError, NotImplementedError) as error:
        pytest.skip(f"Symlink creation unavailable: {error}")
    result = get_changed_python_files(repo)
    assert result["status"] == "passed"
    assert "external.py" not in result["files"]
