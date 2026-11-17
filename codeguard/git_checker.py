
import subprocess
from pathlib import Path

from codeguard.tool_path import resolve_executable


def get_changed_python_files(repo_path="."):
    """Find modified, staged, and untracked Python files."""

    repo = Path(repo_path).resolve()

    if not repo.is_dir():
        return {
            "status": "error",
            "message": "Directory does not exist",
            "files": [],
        }

    git = resolve_executable("git")

    if git is None:
        return {
            "status": "error",
            "message": "Git was not found",
            "files": [],
        }

    def run_git(*args):
        return subprocess.run(
            [str(git), "-C", str(repo), *args],
            capture_output=True,
            stdin=subprocess.DEVNULL,
            timeout=15,
            check=False,
        )

    try:
        check = run_git("rev-parse", "--show-toplevel")

        if check.returncode != 0:
            return {
                "status": "error",
                "message": "Not a Git repository",
                "files": [],
            }

        root = Path(
            check.stdout.decode("utf-8", errors="replace").strip()
        ).resolve()

        # Modified and staged files compared with HEAD.
        tracked = run_git(
            "diff",
            "--name-only",
            "-z",
            "--diff-filter=ACMRT",
            "HEAD",
            "--",
            "*.py",
        )

        if tracked.returncode != 0:
            return {
                "status": "error",
                "message": "Git diff failed",
                "files": [],
            }

        # New files that have not been added to Git.
        untracked = run_git(
            "ls-files",
            "--others",
            "--exclude-standard",
            "-z",
            "--",
            "*.py",
        )

        if untracked.returncode != 0:
            return {
                "status": "error",
                "message": "Git untracked-file detection failed",
                "files": [],
            }

        names = set()

        for output in (tracked.stdout, untracked.stdout):
            for raw_name in output.split(b"\0"):
                if not raw_name:
                    continue

                name = raw_name.decode(
                    "utf-8",
                    errors="surrogateescape",
                )

                if not name.endswith(".py"):
                    continue

                # Git reports paths relative to the supplied
                # directory for these commands.
                candidate = (repo / name).resolve()

                # Do not return files outside the Git repository.
                if not candidate.is_relative_to(root):
                    continue

                if not candidate.is_file():
                    continue

                names.add(candidate.relative_to(repo).as_posix())

        files = sorted(names)

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

    except (OSError, UnicodeError, ValueError) as error:
        return {
            "status": "error",
            "message": str(error),
            "files": [],
        }
