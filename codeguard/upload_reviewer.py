import tempfile
from pathlib import Path

from codeguard.reviewer import review_file

MAX_UPLOAD_BYTES = 2 * 1024 * 1024


def review_uploaded_file(filename, content):
    """Review uploaded Python source without executing it."""
    name = str(filename).replace(chr(92), "/").split("/")[-1]
    if not name or name in (".", "..") or not name.lower().endswith(".py"):
        raise ValueError("A valid Python filename is required")
    if not isinstance(content, bytes):
        raise ValueError("Uploaded content must be bytes")  # noqa: TRY004 - preserve public API
    if len(content) > MAX_UPLOAD_BYTES:
        raise ValueError("Maximum file size is 2 MB")

    with tempfile.TemporaryDirectory(prefix="codeguard_") as directory:
        path = Path(directory) / "uploaded.py"
        path.write_bytes(content)
        review = review_file(path)

    review["file"] = name
    for category in ("quality", "security"):
        for issue in review.get(category, {}).get("issues", []):
            issue["filename"] = name

    return {
        "status": review["status"],
        "message": "1 Python file reviewed",
        "files_reviewed": 1,
        "total_issues": review.get("total_issues", 0),
        "reviews": [review],
    }


MAX_BATCH_FILES = 20
MAX_BATCH_BYTES = 20 * 1024 * 1024


def review_uploaded_files(files, progress=None):
    """Review a bounded batch of (filename, bytes) without executing uploads."""
    items = list(files)
    if not items or len(items) > MAX_BATCH_FILES:
        raise ValueError("Choose between 1 and 20 Python files")
    total = 0
    names = set()
    normalized = []
    for filename, content in items:
        name = str(filename).replace(chr(92), "/").split("/")[-1]
        if not name or name in (".", "..") or not name.lower().endswith(".py"):
            raise ValueError("A valid Python filename is required")
        if not isinstance(content, bytes):
            raise ValueError("Uploaded content must be bytes")  # noqa: TRY004 - preserve public API
        if len(content) > MAX_UPLOAD_BYTES:
            raise ValueError("Maximum file size is 2 MB")
        if name.casefold() in names:
            raise ValueError("Duplicate filenames are not allowed in one batch")
        names.add(name.casefold())
        total += len(content)
        if total > MAX_BATCH_BYTES:
            raise ValueError("Maximum total upload size is 20 MB")
        normalized.append((name, content))
    reviews = []
    for index, (name, content) in enumerate(normalized, 1):
        # Preserve the original single-file public interface.
        reviews.extend(review_uploaded_file(name, content)["reviews"])
        if progress is not None:
            progress(index, len(normalized))
    statuses = [r["status"] for r in reviews]
    status = "error" if "error" in statuses else "issues_found" if "issues_found" in statuses else "passed"
    return {"status": status, "message": f"{len(reviews)} Python file(s) reviewed", "files_reviewed": len(reviews), "total_issues": sum(r.get("total_issues", 0) for r in reviews), "reviews": reviews}
