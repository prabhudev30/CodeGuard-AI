
import subprocess
from pathlib import Path


def get_changed_python_files(repo_path="."):
    """Find tracked Python files changed in a Git repository."""

    repo = Path(repo_path).resolve()

    if not repo.is_dir():
        return {
            "status": "error",
            "message": "Directory does not exist",
            "files": [],
        }

    try:
        check = subprocess.run(
            [
                "git",
                "-C",
                str(repo),
                "rev-parse",
                "--show-toplevel",
            ],
            capture_output=True,
            text=True,
            timeout=15,
            check=False,
        )

        if check.returncode != 0:
            return {
                "status": "error",
                "message": "Not a Git repository",
                "files": [],
            }

        result = subprocess.run(
            [
                "git",
                "-C",
                str(repo),
                "diff",
                "--name-only",
                "--diff-filter=ACMRT",
                "HEAD",
                "--",
                "*.py",
            ],
            capture_output=True,
            text=True,
            timeout=15,
            check=False,
        )

        if result.returncode != 0:
            return {
                "status": "error",
                "message": result.stderr.strip()
                or "Git diff failed",
                "files": [],
            }

        files = [
            name
            for name in result.stdout.splitlines()
            if name.endswith(".py")
        ]

        return {
            "status": "passed",
            "message": f"{len(files)} changed Python file(s)",
            "files": files,
        }

    except subprocess.TimeoutExpired:
        return {
            "status": "error",
            "message": "Git operation timed out",
            "files": [],
        }

    except OSError as error:
        return {
            "status": "error",
            "message": str(error),
            "files": [],
        }
