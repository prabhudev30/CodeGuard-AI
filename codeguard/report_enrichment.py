from codeguard.issue_formatter import format_issue, explain_issue, calculate_priority


def enrich_issue(issue, category):
    row = format_issue(issue, category)
    rule = issue.get("test_id") or issue.get("code") or "N/A"
    return {**row, "Category": category.title(), "Priority": calculate_priority(issue, category), **explain_issue(rule)}


def enrich_review(review):
    enriched = []
    for file_review in review.get("reviews", []):
        findings = []
        for category in ("quality", "security"):
            for issue in (file_review.get(category) or {}).get("issues", []):
                findings.append(enrich_issue(issue, category))
        enriched.append({"file": file_review.get("file", "Unknown file"), "findings": findings})
    return enriched
