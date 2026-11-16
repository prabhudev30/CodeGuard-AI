
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

    command = [
        sys.executable,
        "-m",
        "bandit",
        "-f",
        "json",
        "-q",
        str(path),
    ]
    
    if skip_assert_checks:
        command.extend(["-s", "B101"])

    try:
        result = subprocess.run(
            command,
            capture_output=True,
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

        report = json.loads(result.stdout)
        issues = report.get("results", [])

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
