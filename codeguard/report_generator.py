

import json
import os
import tempfile
from datetime import UTC, datetime
from pathlib import Path

from codeguard.health_score import score_review
from codeguard.report_enrichment import enrich_review


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
            "app_version": "1.3.0",
            "schema_version": "1.3",
            "health": score_review(review_result),
            "review_mode": review_result.get("review_mode", "unspecified"),
            "generated_at": datetime.now(UTC).isoformat(),
            "review": review_result,
            "enriched_findings": enrich_review(review_result),
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
