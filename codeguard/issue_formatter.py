
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


ISSUE_GUIDANCE = {
    "F401": ("Unused import", "Remove the import if it is not needed."),
    "F821": ("Undefined name", "Define the missing name or correct its spelling."),
    "B101": ("Assert in production code", "Use explicit validation rather than assert for security checks."),
    "B602": ("Shell command execution", "Avoid shell=True with untrusted input; use an argument list."),
    "B603": ("Subprocess execution", "Check that command arguments cannot be controlled by untrusted input."),
    "B404": ("Subprocess module", "Review subprocess usage and avoid unsafe command execution."),
}


def explain_issue(code):
    title, fix = ISSUE_GUIDANCE.get(code, ("Unrecognized rule", "Review the analyzer message and rule documentation."))
    return {"Explanation": title, "Suggested Fix": fix}
