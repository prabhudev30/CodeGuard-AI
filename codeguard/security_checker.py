
import importlib.util
import json
import subprocess
import sys
from pathlib import Path


def check_security(file_path, skip_assert_checks=False):
    """Scan a Python file for potential security issues."""

    path = Path(file_path)

    if not path.is_file():
        return {
            "status": "error",
            "message": "File does not exist",
            "issues": [],
        }

    if importlib.util.find_spec("bandit") is None:
        return {
            "status": "error",
            "message": "Bandit was not found",
            "issues": [],
        }

    command = [
        sys.executable,
        "-m",
        "bandit",
        "-f",
        "json",
        "-q",
    ]

    if skip_assert_checks:
        command.extend(["-s", "B101"])

    command.extend(["--", str(path)])

    try:
        result = subprocess.run(
            command,
            capture_output=True,
            stdin=subprocess.DEVNULL,
            text=True,
            timeout=30,
            check=False,
        )

        if result.returncode not in (0, 1):
            return {
                "status": "error",
                "message": result.stderr.strip()
                or "Bandit execution failed",
                "issues": [],
            }

        try:
            report = json.loads(result.stdout)
        except json.JSONDecodeError:
            return {
                "status": "error",
                "message": "Bandit returned invalid output",
                "issues": [],
            }

        issues = report.get("results", []) if isinstance(report, dict) else None

        if not isinstance(issues, list):
            return {
                "status": "error",
                "message": "Bandit returned invalid output",
                "issues": [],
            }

        return {
            "status": "passed" if not issues else "issues_found",
            "message": f"{len(issues)} security issue(s) found",
            "issues": issues,
        }

    except subprocess.TimeoutExpired:
        return {
            "status": "error",
            "message": "Bandit analysis timed out",
            "issues": [],
        }

    except (OSError, ValueError) as error:
        return {
            "status": "error",
            "message": str(error),
            "issues": [],
        }
