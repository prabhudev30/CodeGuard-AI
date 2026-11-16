def format_syntax_finding(file_review):
    """Convert a failed syntax check into a dashboard finding."""
    syntax = file_review.get("syntax") or {}
    if syntax.get("status") == "passed":
        return None
    if syntax.get("status") not in ("failed", "error"):
        return None
    return {
        "File": file_review.get("file", "Unknown file"),
        "Category": "Syntax",
        "Code": "SYNTAX",
        "Severity": "error",
        "Line": syntax.get("line") or "N/A",
        "Description": syntax.get("message", "Syntax check failed"),
        "Priority": "High" if syntax.get("status") == "failed" else "Review",
        "Explanation": "Python syntax error" if syntax.get("status") == "failed" else "Syntax check could not complete",
        "Suggested Fix": "Correct the Python syntax at the reported line." if syntax.get("status") == "failed" else "Check that the file exists and can be read.",
    }
