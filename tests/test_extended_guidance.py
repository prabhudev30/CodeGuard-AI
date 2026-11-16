import pytest
from codeguard.issue_formatter import ISSUE_GUIDANCE, explain_issue


NEW_RULES = ("F811", "F841", "F823", "E402", "E701", "E702", "E703", "E711", "B102", "B307")


@pytest.mark.parametrize("rule", NEW_RULES)
def test_new_rule_has_guidance(rule):
    result = explain_issue(rule)
    assert result["Explanation"] != "Unrecognized rule"
    assert result["Suggested Fix"]
    assert rule in ISSUE_GUIDANCE


def test_all_guidance_entries_are_complete():
    assert len(ISSUE_GUIDANCE) == 16
    assert all(title and fix for title, fix in ISSUE_GUIDANCE.values())
