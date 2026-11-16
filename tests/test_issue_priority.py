from codeguard.issue_formatter import calculate_priority


def test_security_priorities():
    for severity, expected in [("HIGH", "High"), ("MEDIUM", "Medium"), ("LOW", "Low")]:
        assert calculate_priority({"issue_severity": severity}, "security") == expected


def test_quality_priorities():
    assert calculate_priority({"code": "F821"}, "quality") == "High"
    assert calculate_priority({"code": "F401"}, "quality") == "Low"


def test_unknown_priority():
    assert calculate_priority({}, "security") == "Review"
    assert calculate_priority({}, "quality") == "Review"
