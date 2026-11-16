from codeguard.report_enrichment import enrich_issue, enrich_review


def test_quality_issue_enrichment():
    issue = {"code": "F821", "severity": "error", "location": {"row": 6}, "message": "Undefined name"}
    result = enrich_issue(issue, "quality")
    assert result["Code"] == "F821"
    assert result["Line"] == 6
    assert result["Priority"] == "High"
    assert result["Explanation"] == "Undefined name"
    assert result["Suggested Fix"]


def test_security_issue_enrichment():
    issue = {"test_id": "B602", "issue_severity": "HIGH", "line_number": 4, "issue_text": "Shell execution"}
    result = enrich_issue(issue, "security")
    assert result["Code"] == "B602"
    assert result["Priority"] == "High"
    assert result["Category"] == "Security"
    assert result["Suggested Fix"]


def test_review_enrichment_preserves_file():
    review = {"reviews": [{"file": "sample.py", "quality": {"issues": [{"code": "F401", "message": "Unused import", "location": {"row": 1}}]}, "security": {"issues": []}}]}
    result = enrich_review(review)
    assert result[0]["file"] == "sample.py"
    assert result[0]["findings"][0]["Priority"] == "Low"


def test_empty_review():
    assert enrich_review({"reviews": []}) == []
