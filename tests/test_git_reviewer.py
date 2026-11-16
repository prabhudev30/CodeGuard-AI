
import subprocess

from codeguard.git_reviewer import review_changed_files


def git(folder, *args):
    return subprocess.run(
        ["git", "-C", str(folder), *args],
        capture_output=True,
        text=True,
        check=True,
    )


def make_repo(folder):
    git(folder, "init")
    git(folder, "config", "user.name", "CodeGuard Test")
    git(folder, "config", "user.email", "test@example.com")

    file = folder / "sample.py"
    file.write_text("print('hello')\n", encoding="utf-8")

    git(folder, "add", "sample.py")
    git(folder, "commit", "-m", "Initial commit")

    return file


def test_no_changed_files(tmp_path):
    make_repo(tmp_path)

    result = review_changed_files(tmp_path)

    assert result["status"] == "passed"
    assert result["files_reviewed"] == 0
    assert result["total_issues"] == 0


def test_changed_clean_file(tmp_path):
    file = make_repo(tmp_path)
    file.write_text("print('updated')\n", encoding="utf-8")

    result = review_changed_files(tmp_path)

    assert result["status"] == "passed"
    assert result["files_reviewed"] == 1
    assert result["total_issues"] == 0


def test_changed_quality_issue(tmp_path):
    file = make_repo(tmp_path)
    file.write_text(
        "import os\nprint('updated')\n",
        encoding="utf-8",
    )

    result = review_changed_files(tmp_path)

    assert result["status"] == "issues_found"
    assert result["files_reviewed"] == 1
    assert result["total_issues"] >= 1


def test_changed_syntax_issue(tmp_path):
    file = make_repo(tmp_path)
    file.write_text("def broken(:\n", encoding="utf-8")

    result = review_changed_files(tmp_path)

    assert result["status"] == "issues_found"
    assert result["files_reviewed"] == 1
    assert result["total_issues"] >= 1


def test_invalid_repository(tmp_path):
    result = review_changed_files(tmp_path)

    assert result["status"] == "error"
    assert result["files_reviewed"] == 0
    assert result["total_issues"] == 0
