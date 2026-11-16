
from pathlib import Path

from codeguard.git_checker import get_changed_python_files
from codeguard.reviewer import review_file


def review_changed_files(repo_path="."):
    """Review changed Python files in a Git repository."""

    repo = Path(repo_path).resolve()

    changes = get_changed_python_files(repo)

    if changes["status"] != "passed":
        return {
            "status": "error",
            "message": changes["message"],
            "files_reviewed": 0,
            "total_issues": 0,
            "reviews": [],
        }

    reviews = []

    for filename in changes["files"]:
        file_path = repo / filename

        result = review_file(file_path)
        reviews.append(result)

    total_issues = sum(
        review.get("total_issues", 0)
        for review in reviews
    )

    statuses = [review["status"] for review in reviews]

    if "error" in statuses:
        overall_status = "error"
    elif "issues_found" in statuses:
        overall_status = "issues_found"
    else:
        overall_status = "passed"

    return {
        "status": overall_status,
        "message": f"{len(reviews)} Python file(s) reviewed",
        "files_reviewed": len(reviews),
        "total_issues": total_issues,
        "reviews": reviews,
    }
