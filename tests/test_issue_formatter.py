
from codeguard.issue_formatter import format_issue


def test_bandit_rule_id():
    issue = {
        "code": "import subprocess",
        "test_id": "B404",
        "issue_severity": "LOW",
        "line_number": 2,
        "issue_text": "Security implications of subprocess",
    }

    row = format_issue(issue, "security")

    assert row["Code"] == "B404"
    assert row["Severity"] == "LOW"
    assert row["Line"] == 2


def test_ruff_rule_id():
    issue = {
        "code": "F401",
        "severity": "error",
        "location": {"row": 3},
        "message": "Unused import",
    }

    row = format_issue(issue, "quality")

    assert row["Code"] == "F401"
    assert row["Line"] == 3
    assert row["Description"] == "Unused import"


def test_missing_fields():
    row = format_issue({}, "security")

    assert row["Code"] == "N/A"
    assert row["Severity"] == "N/A"
    assert row["Line"] == "N/A"
