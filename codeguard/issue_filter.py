def filter_findings(findings, category="All", priority="All", search=""):
    """Filter enriched issue rows without modifying the originals."""
    term = str(search or "").strip().casefold()
    result = []
    for finding in findings:
        if category != "All" and str(finding.get("Category", "")).casefold() != category.casefold():
            continue
        if priority != "All" and str(finding.get("Priority", "")).casefold() != priority.casefold():
            continue
        searchable = " ".join(str(finding.get(key, "")) for key in ("Code", "Description", "File", "Explanation", "Suggested Fix"))
        if term and term not in searchable.casefold():
            continue
        result.append(finding)
    return result
