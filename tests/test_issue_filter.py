from codeguard.issue_filter import filter_findings


def sample_findings():
    return [
        dict(File="main.py", Category="Quality", Priority="High", Code="F821", Description="Undefined variable"),
        dict(File="auth.py", Category="Security", Priority="High", Code="B602", Description="Shell execution"),
        dict(File="main.py", Category="Quality", Priority="Low", Code="F401", Description="Unused import"),
    ]


def test_all_findings():
    assert len(filter_findings(sample_findings())) == 3


def test_category_filter():
    result = filter_findings(sample_findings(), category="Security")
    assert len(result) == 1
    assert result[0]["Code"] == "B602"


def test_priority_filter():
    result = filter_findings(sample_findings(), priority="High")
    assert len(result) == 2


def test_search_rule_code():
    result = filter_findings(sample_findings(), search="f821")
    assert len(result) == 1


def test_search_filename():
    result = filter_findings(sample_findings(), search="auth.py")
    assert len(result) == 1


def test_combined_filters():
    result = filter_findings(sample_findings(), category="Quality", priority="Low", search="import")
    assert len(result) == 1
    assert result[0]["Code"] == "F401"


def test_no_matches():
    assert filter_findings(sample_findings(), search="nonexistent") == []


def test_does_not_modify_original():
    findings = sample_findings()
    original = [dict(item) for item in findings]
    filter_findings(findings, category="Security")
    assert findings == original
