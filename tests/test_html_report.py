
import json

from codeguard.html_report import generate_html_report


def make_json_report(tmp_path, review):
    source = tmp_path / "report.json"
    source.write_text(
        json.dumps({
            "tool": "CodeGuard AI",
            "generated_at": "2026-11-16T12:00:00+00:00",
            "review": review,
        }),
        encoding="utf-8",
    )
    return source


def test_valid_html_report(tmp_path):
    source = make_json_report(tmp_path, {
        "status": "passed",
        "files_reviewed": 0,
        "total_issues": 0,
        "reviews": [],
    })

    output = tmp_path / "report.html"
    result = generate_html_report(source, output)

    assert result["status"] == "passed"
    assert output.exists()

    content = output.read_text(encoding="utf-8")
    assert "CodeGuard AI" in content
    assert "No changed files were reviewed" in content


def test_quality_issue_displayed(tmp_path):
    source = make_json_report(tmp_path, {
        "status": "issues_found",
        "files_reviewed": 1,
        "total_issues": 1,
        "reviews": [{
            "file": "example.py",
            "status": "issues_found",
            "syntax": {"status": "passed"},
            "quality": {
                "issues": [{
                    "code": "F401",
                    "message": "Unused import",
                    "location": {"row": 3},
                }],
            },
            "security": {"issues": []},
        }],
    })

    output = tmp_path / "report.html"
    result = generate_html_report(source, output)

    assert result["status"] == "passed"

    content = output.read_text(encoding="utf-8")
    assert "F401" in content
    assert "Unused import" in content
    assert "<td>3</td>" in content


def test_html_escaping(tmp_path):
    malicious = "<script>alert('test')</script>"

    source = make_json_report(tmp_path, {
        "status": "issues_found",
        "files_reviewed": 1,
        "total_issues": 1,
        "reviews": [{
            "file": malicious,
            "status": "issues_found",
            "syntax": {"status": "passed"},
            "quality": {
                "issues": [{
                    "code": "F821",
                    "message": malicious,
                    "location": {"row": 1},
                }],
            },
            "security": {"issues": []},
        }],
    })

    output = tmp_path / "report.html"
    result = generate_html_report(source, output)

    assert result["status"] == "passed"

    content = output.read_text(encoding="utf-8")

    assert malicious not in content
    assert "&lt;script&gt;" in content


def test_missing_json_file(tmp_path):
    result = generate_html_report(
        tmp_path / "missing.json",
        tmp_path / "report.html",
    )

    assert result["status"] == "error"


def test_invalid_json_file(tmp_path):
    source = tmp_path / "invalid.json"
    source.write_text("{invalid json", encoding="utf-8")

    result = generate_html_report(
        source,
        tmp_path / "report.html",
    )

    assert result["status"] == "error"
