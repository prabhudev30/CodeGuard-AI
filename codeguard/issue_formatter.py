
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


# Offline, illustrative examples only; never execute analyzed code.
ISSUE_EXAMPLES = {
    "F401": ("import os\nprint('Hello')", "print('Hello')"),
    "F821": ("print(username)", "username = 'Alice'\nprint(username)"),
    "F841": ("def greet():\n    unused = 42\n    print('Hi')", "def greet():\n    print('Hi')"),
    "E402": ("print('Start')\nimport os", "import os\n\nprint('Start')"),
    "E711": ("if value == None:\n    print('Missing')", "if value is None:\n    print('Missing')"),
    "E701": ("if ready: print('Go')", "if ready:\n    print('Go')"),
    "E702": ("x = 1; y = 2", "x = 1\ny = 2"),
    "B101": ("assert user_is_admin", "if not user_is_admin:\n    raise PermissionError('Access denied')"),
    "B602": ("subprocess.run('echo hello', shell=True)", "subprocess.run(['echo', 'hello'], check=True)"),
    "B603": ("subprocess.run([user_supplied_program])", "# Validate the executable and arguments against an allowlist\nsubprocess.run([trusted_executable], check=True)"),
    "B307": ("value = eval(user_input)", "import ast\nvalue = ast.literal_eval(user_input)  # Only for Python literals"),
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
    before, after = ISSUE_EXAMPLES.get(code, ("", ""))
    return {"Explanation": title, "Suggested Fix": fix, "Why It Matters": details.get(code, "This finding may affect correctness, maintainability, or security; inspect the analyzer message."), "Example": before, "Corrected Example": after}


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
