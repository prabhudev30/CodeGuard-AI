from codeguard.syntax_findings import format_syntax_finding


def test_failed_syntax():
    review = dict(file="broken.py", syntax=dict(status="failed", message="invalid syntax", line=7))
    row = format_syntax_finding(review)
    assert row["Category"] == "Syntax"
    assert row["Line"] == 7
    assert row["Priority"] == "High"


def test_passed_syntax():
    assert format_syntax_finding(dict(syntax=dict(status="passed"))) is None


def test_unreadable_file():
    row = format_syntax_finding(dict(file="missing.py", syntax=dict(status="error", message="File does not exist")))
    assert row["Priority"] == "Review"
    assert row["File"] == "missing.py"


def test_missing_syntax_result():
    assert format_syntax_finding(dict(file="example.py")) is None
