import json

from codeguard.html_report import generate_html_report
from codeguard.report_generator import save_json_report


def test_json_export_enrichment(tmp_path):
    review = {"reviews": [{"file": "example.py", "quality": {"issues": [{"code": "F821", "message": "Undefined name", "location": {"row": 6}}]}, "security": {"issues": []}}]}
    path = tmp_path / "report.json"
    assert save_json_report(review, path)["status"] == "passed"
    data = json.loads(path.read_text(encoding="utf-8"))
    assert data["review"] == review
    assert data["enriched_findings"][0]["findings"][0]["Priority"] == "High"


def test_html_export_enrichment_and_escaping(tmp_path):
    malicious = chr(60) + "script" + chr(62) + "alert(1)" + chr(60) + "/script" + chr(62)
    review = {"status": "issues_found", "files_reviewed": 1, "total_issues": 2, "reviews": [{"file": "example.py", "status": "issues_found", "syntax": {"status": "passed"}, "quality": {"issues": [{"code": "F821", "message": malicious, "location": {"row": 6}}]}, "security": {"issues": [{"test_id": "B602", "issue_severity": "HIGH", "line_number": 8, "issue_text": "Shell execution"}]}}]}
    source = tmp_path / "report.json"
    output = tmp_path / "report.html"
    assert save_json_report(review, source)["status"] == "passed"
    assert generate_html_report(source, output)["status"] == "passed"
    page = output.read_text(encoding="utf-8")
    assert all(x in page for x in ("F821", "B602", "High", "Suggested Fix", "Explanation"))
    assert malicious not in page
    assert (chr(38) + "lt;script" + chr(38) + "gt;") in page


def test_html_syntax_row_has_nine_cells(tmp_path):
    review = {"status": "issues_found", "files_reviewed": 1, "total_issues": 1, "reviews": [{"file": "broken.py", "status": "issues_found", "syntax": {"status": "error", "message": "Invalid syntax"}, "quality": {"issues": []}, "security": {"issues": []}}]}
    source = tmp_path / "report.json"
    output = tmp_path / "report.html"
    assert save_json_report(review, source)["status"] == "passed"
    assert generate_html_report(source, output)["status"] == "passed"
    page = output.read_text(encoding="utf-8")
    start = page.index(chr(60) + "td" + chr(62) + "Syntax")
    row = page[start:page.index(chr(60) + "/tr" + chr(62), start)]
    assert row.count(chr(60) + "td" + chr(62)) == 9
