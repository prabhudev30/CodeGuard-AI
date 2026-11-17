
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
    "F811": ("Redefined name", "Remove the duplicate definition or use a different name."),
    "F841": ("Unused variable", "Remove the variable or use its assigned value."),
    "F823": ("Local variable referenced before assignment", "Assign the variable before reading it in the local scope."),
    "E402": ("Import not at top of file", "Move imports to the top of the module where practical."),
    "E701": ("Multiple statements on one line", "Place each statement on its own line."),
    "E702": ("Multiple statements separated by semicolon", "Split the statements onto separate lines."),
    "E703": ("Unnecessary semicolon", "Remove the unnecessary semicolon."),
    "E711": ("Incorrect comparison with None", "Use is None or is not None instead of equality comparison."),
    "B102": ("Use of exec", "Avoid executing dynamic Python code, especially from untrusted input."),
    "B307": ("Use of eval", "Avoid eval on untrusted expressions; use a safer parser when appropriate."),
}


def explain_issue(code):
    title, fix = ISSUE_GUIDANCE.get(code, ("Unrecognized rule", "Review the analyzer message and rule documentation."))
    details = {
        "F401": "Unused imports add clutter and can hide mistakes.",
        "F821": "A missing name can raise NameError when the code runs.",
        "F841": "Unused variables may indicate incomplete logic.",
        "B307": "eval can execute dangerous expressions when input is untrusted.",
        "B602": "Shell execution can be exploited when arguments are untrusted.",
        "E722": "A bare except may hide important failures.",
    }
    return {"Explanation": title, "Suggested Fix": fix, "Why It Matters": details.get(code, "This finding may affect correctness, maintainability, or security; inspect the analyzer message."), "Example": "", "Corrected Example": ""}


def calculate_priority(issue, category):
    if category == "security":
        severity = str(issue.get("issue_severity") or "").upper()
        return {"HIGH": "High", "MEDIUM": "Medium", "LOW": "Low"}.get(severity, "Review")
    if category == "quality":
        code = issue.get("code")
        if code in ("F821", "E999"):
            return "High"
        if code == "F401":
            return "Low"
    return "Review"
