

import json
import os
import tempfile
from datetime import datetime, timezone
from pathlib import Path


def save_json_report(review_result, output_path="reports/codeguard_report.json"):
    """Safely save a CodeGuard review result as JSON."""

    if not isinstance(review_result, dict):
        return {
            "status": "error",
            "message": "Review result must be a dictionary",
        }

    temp_path = None

    try:
        path = Path(output_path)

        report = {
            "tool": "CodeGuard AI",
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "review": review_result,
        }

        # Validate the entire JSON before touching the destination.
        content = json.dumps(
            report,
            indent=4,
            ensure_ascii=False,
        )

        path.parent.mkdir(parents=True, exist_ok=True)

        # Create a temporary file in the destination directory.
        with tempfile.NamedTemporaryFile(
            mode="w",
            encoding="utf-8",
            dir=path.parent,
            prefix=".codeguard_",
            suffix=".tmp",
            delete=False,
        ) as temp_file:
            temp_path = Path(temp_file.name)
            temp_file.write(content)

        # Replace the destination only after writing succeeds.
        os.replace(temp_path, path)
        temp_path = None

        return {
            "status": "passed",
            "message": "JSON report saved successfully",
            "path": str(path.resolve()),
        }

    except (OSError, TypeError, ValueError) as error:
        return {
            "status": "error",
            "message": str(error),
        }

    finally:
        if temp_path is not None:
            try:
                temp_path.unlink(missing_ok=True)
            except OSError:
                pass
