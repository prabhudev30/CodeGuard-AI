from codeguard.issue_formatter import explain_issue


def test_known_quality_rule():
    result = explain_issue("F821")
    assert result["Explanation"] == "Undefined name"
    assert "Define" in result["Suggested Fix"]


def test_known_security_rule():
    result = explain_issue("B602")
    assert result["Explanation"] == "Shell command execution"
    assert "shell=True" in result["Suggested Fix"]


def test_unknown_rule_has_fallback():
    result = explain_issue("UNKNOWN")
    assert result["Explanation"] == "Unrecognized rule"
    assert result["Suggested Fix"]
