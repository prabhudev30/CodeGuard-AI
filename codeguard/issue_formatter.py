
def format_issue(issue, category):
    """Convert Ruff or Bandit findings into dashboard table rows."""

    location = issue.get("location") or {}

    if category == "security":
        return {
            "Code": issue.get("test_id", "N/A"),
            "Severity": issue.get("issue_severity", "N/A"),
            "Line": issue.get("line_number", "N/A"),
            "Description": issue.get("issue_text", ""),
        }

    return {
        "Code": issue.get("code", "N/A"),
        "Severity": issue.get("severity", "N/A"),
        "Line": issue.get("line_number", location.get("row", "N/A")),
        "Description": issue.get("message", ""),
    }
