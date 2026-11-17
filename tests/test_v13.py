import json
import pytest
from codeguard.upload_reviewer import review_uploaded_files, MAX_UPLOAD_BYTES
from codeguard.health_score import score_file, score_review
from codeguard.issue_formatter import explain_issue
from codeguard.report_generator import save_json_report
from codeguard.html_report import generate_html_report


def test_batch_review():
    result = review_uploaded_files([("one.py", b"print(1)\n"), ("two.py", b"print(missing_name)\n")])
    assert result["files_reviewed"] == 2
    assert [r["file"] for r in result["reviews"]] == ["one.py", "two.py"]
    assert result["total_issues"] >= 1


@pytest.mark.parametrize("items", [[], [("x.py", b"")] * 21, [("x.py", b""), ("x.py", b"")], [("x.txt", b"x")], [("x.py", "text")], [("x.py", b"a" * (MAX_UPLOAD_BYTES + 1))]])
def test_batch_rejects_invalid(items):
    with pytest.raises(ValueError):
        review_uploaded_files(items)


def test_score_clean_and_error():
    clean = {"status": "passed", "syntax": {"status": "passed"}, "quality": {"status": "passed", "issues": []}, "security": {"status": "passed", "issues": []}}
    assert score_file(clean)["overall"] == 100
    assert score_file({"status": "error"}) is None
    assert score_review({"reviews": [clean]})["overall"] == 100


def test_score_high_finding():
    review = {"status": "issues_found", "syntax": {"status": "passed"}, "quality": {"status": "issues_found", "issues": [{"code": "F821"}]}, "security": {"status": "passed", "issues": []}}
    assert score_file(review)["overall"] == 85


def test_explanations():
    assert "Why It Matters" in explain_issue("F821")
    assert "Suggested Fix" in explain_issue("unknown")


def test_report_health(tmp_path):
    result = review_uploaded_files([("x.py", b"print(1)\n")])
    jp, hp = tmp_path / "out.json", tmp_path / "out.html"
    assert save_json_report(result, jp)["status"] == "passed"
    report = json.loads(jp.read_text(encoding="utf-8"))
    assert report["schema_version"] == "1.3"
    assert report["health"]["overall"] is not None
    assert generate_html_report(jp, hp)["status"] == "passed"
    assert "Health Score" in hp.read_text(encoding="utf-8")
