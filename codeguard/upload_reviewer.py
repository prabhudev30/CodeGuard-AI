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
        raise ValueError("Uploaded content must be bytes")
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
