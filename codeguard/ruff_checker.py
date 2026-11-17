
import json
import subprocess
from pathlib import Path

from codeguard.tool_path import resolve_executable


def check_code_quality(file_path):
    """Analyze a Python file using Ruff."""

    path = Path(file_path)

    if not path.is_file():
        return {
            "status": "error",
            "message": "File does not exist",
            "issues": [],
        }

    ruff = resolve_executable("ruff")

    if ruff is None:
        return {
            "status": "error",
            "message": "Ruff was not found",
            "issues": [],
        }

    command = [
        str(ruff),
        "check",
        "--output-format",
        "json",
        "--no-cache",
        "--select",
        "E4,E7,E9,F",
        "--",
        str(path),
    ]

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
                or "Ruff execution failed",
                "issues": [],
            }

        try:
            issues = json.loads(result.stdout)
        except json.JSONDecodeError:
            return {
                "status": "error",
                "message": "Ruff returned invalid output",
                "issues": [],
            }

        if not isinstance(issues, list):
            return {
                "status": "error",
                "message": "Ruff returned invalid output",
                "issues": [],
            }

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
