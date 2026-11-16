
import json

from codeguard.report_generator import save_json_report


def test_save_valid_report(tmp_path):
    output = tmp_path / "report.json"

    result = save_json_report(
        {"status": "passed", "total_issues": 0},
        output,
    )

    assert result["status"] == "passed"
    assert output.exists()

    data = json.loads(output.read_text(encoding="utf-8"))
    assert data["tool"] == "CodeGuard AI"
    assert data["review"]["total_issues"] == 0
    assert "generated_at" in data


def test_nested_directory_creation(tmp_path):
    output = tmp_path / "nested" / "reports" / "report.json"

    result = save_json_report(
        {"status": "issues_found", "total_issues": 2},
        output,
    )

    assert result["status"] == "passed"
    assert output.exists()


def test_invalid_review_input(tmp_path):
    output = tmp_path / "invalid.json"

    result = save_json_report("not a dictionary", output)

    assert result["status"] == "error"
    assert not output.exists()


def test_unserializable_review_input(tmp_path):
    output = tmp_path / "invalid.json"

    result = save_json_report(
        {"bad_value": {1, 2, 3}},
        output,
    )

    assert result["status"] == "error"


def test_output_path_is_directory(tmp_path):
    result = save_json_report(
        {"status": "passed"},
        tmp_path,
    )

    assert result["status"] == "error"
