import json

import pytest

from codeguard.html_report import generate_html_report
from codeguard.issue_formatter import ISSUE_EXAMPLES, explain_issue
from codeguard.report_enrichment import enrich_issue


@pytest.mark.parametrize("code", ["F401", "F821", "F841", "E402", "E711", "E701", "E702", "B101", "B602", "B603", "B307"])
def test_examples_are_present_and_distinct(code):
    guidance = explain_issue(code)
    assert guidance["Example"]
    assert guidance["Corrected Example"]
    assert guidance["Example"] != guidance["Corrected Example"]
    assert {"Explanation", "Suggested Fix", "Why It Matters", "Example", "Corrected Example"} <= guidance.keys()


def test_unknown_rule_keeps_fallback():
    guidance = explain_issue("ZZ999")
    assert guidance["Explanation"] == "Unrecognized rule"
    assert guidance["Example"] == ""
    assert guidance["Corrected Example"] == ""


def test_enrichment_includes_examples():
    result = enrich_issue({"code": "F821", "message": "undefined name", "location": {"row": 2}}, "quality")
    assert result["Example"] == ISSUE_EXAMPLES["F821"][0]


def test_html_examples_escaped_and_no_code_execution(tmp_path, monkeypatch):
    import codeguard.issue_formatter as formatter
    monkeypatch.setitem(formatter.ISSUE_EXAMPLES, "F821", ("<script>alert(1)</script>", "x = '<unsafe>'"))
    data = {"review": {"status": "completed", "files_reviewed": 1, "total_issues": 1,
                       "reviews": [{"file": "sample.py", "status": "completed",
                                    "quality": {"issues": [{"code": "F821", "message": "undefined name", "location": {"row": 1}}]},
                                    "security": {"issues": []}, "syntax": {"status": "passed"}}]},
            "health": {"overall": 90, "quality": 90, "security": 100, "syntax": 100}}
    source = tmp_path / "input.json"
    output = tmp_path / "output.html"
    source.write_text(json.dumps(data), encoding="utf-8")
    assert generate_html_report(source, output)["status"] == "passed"
    page = output.read_text(encoding="utf-8")
    assert "<pre><code>" in page
    assert "&lt;script&gt;alert(1)&lt;/script&gt;" in page
    assert "<script>alert(1)</script>" not in page
    assert "&lt;unsafe&gt;" in page
    assert 'colspan="9"' not in page


def test_html_empty_report_keeps_nine_column_layout(tmp_path):
    data = {"review": {"status": "completed", "files_reviewed": 1, "total_issues": 0,
                       "reviews": [{"file": "clean.py", "status": "completed", "quality": {"issues": []},
                                    "security": {"issues": []}, "syntax": {"status": "passed"}}]},
            "health": {"overall": 100, "quality": 100, "security": 100, "syntax": 100}}
    source, output = tmp_path / "input.json", tmp_path / "output.html"
    source.write_text(json.dumps(data), encoding="utf-8")
    assert generate_html_report(source, output)["status"] == "passed"
    assert 'colspan="9"' in output.read_text(encoding="utf-8")
