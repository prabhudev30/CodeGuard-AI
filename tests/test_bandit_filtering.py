from codeguard.security_checker import check_security


def test_assert_detected_by_default(tmp_path):
    file = tmp_path / "production.py"
    file.write_text("assert True\n", encoding="utf-8")
    result = check_security(file)
    assert "B101" in {issue["test_id"] for issue in result["issues"]}


def test_assert_can_be_skipped(tmp_path):
    file = tmp_path / "test_sample.py"
    file.write_text("assert True\n", encoding="utf-8")
    result = check_security(file, skip_assert_checks=True)
    assert "B101" not in {issue["test_id"] for issue in result["issues"]}


def test_other_security_rules_remain_active(tmp_path):
    file = tmp_path / "test_security.py"
    file.write_text("import subprocess\nsubprocess.run('echo hello', shell=True)\nassert True\n", encoding="utf-8")
    result = check_security(file, skip_assert_checks=True)
    codes = {issue["test_id"] for issue in result["issues"]}
    assert "B602" in codes
    assert "B101" not in codes
