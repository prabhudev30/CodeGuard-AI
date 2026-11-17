
from pathlib import Path

from codeguard.ruff_checker import check_code_quality
from codeguard.security_checker import check_security
from codeguard.syntax_checker import check_syntax


def review_file(file_path, skip_assert_checks=False):
    """Run all CodeGuard analyzers on one Python file."""

    path = Path(file_path)

    if not path.is_file():
        return {
            "file": str(path),
            "status": "error",
            "message": "File does not exist",
        }

    syntax = check_syntax(path)
    quality = check_code_quality(path)
    security = check_security(path, skip_assert_checks=skip_assert_checks)

    results = {
        "file": str(path),
        "syntax": syntax,
        "quality": quality,
        "security": security,
    }

    statuses = [
        syntax["status"],
        quality["status"],
        security["status"],
    ]

    if "error" in statuses:
        results["status"] = "error"
    elif "failed" in statuses or "issues_found" in statuses:
        results["status"] = "issues_found"
    else:
        results["status"] = "passed"

    results["total_issues"] = (
        (1 if syntax["status"] == "failed" else 0)
        + len(quality.get("issues", []))
        + len(security.get("issues", []))
    )

    return results
