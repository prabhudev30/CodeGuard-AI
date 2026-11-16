
import json
import subprocess
from pathlib import Path


def check_code_quality(file_path):
    """Analyze a Python file using Ruff."""

    path = Path(file_path)

    if not path.is_file():
        return {
            "status": "error",
            "message": "File does not exist",
            "issues": [],
        }

    command = [
        "ruff",
        "check",
        "--output-format",
        "json",
        "--no-cache",
        "--select",
        "E4,E7,E9,F",
        str(path),
    ]

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
                or "Ruff execution failed",
                "issues": [],
            }

        issues = json.loads(result.stdout)

        return {
            "status": "passed" if not issues else "issues_found",
            "message": f"{len(issues)} issue(s) found",
            "issues": issues,
        }

    except subprocess.TimeoutExpired:
        return {
            "status": "error",
            "message": "Ruff analysis timed out",
            "issues": [],
        }

    except (OSError, ValueError) as error:
        return {
            "status": "error",
            "message": str(error),
            "issues": [],
        }
