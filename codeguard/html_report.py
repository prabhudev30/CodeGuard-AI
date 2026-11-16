
import html
import json
from pathlib import Path


def escape(value):
    """Safely escape text for HTML."""
    return html.escape(str(value), quote=True)


def generate_html_report(
    json_path="reports/codeguard_report.json",
    output_path="reports/codeguard_report.html",
):
    """Generate a standalone HTML report from a JSON report."""

    try:
        source = Path(json_path)
        data = json.loads(source.read_text(encoding="utf-8"))

        review = data["review"]
        reviews = review.get("reviews", [])

        sections = []

        for file_review in reviews:
            filename = escape(file_review.get("file", "Unknown file"))
            status = escape(file_review.get("status", "unknown"))

            issue_rows = []

            for category in ("quality", "security"):
                category_result = file_review.get(category, {})

                for issue in category_result.get("issues", []):
                    code = escape(issue.get("code", issue.get("test_id", "N/A")))
                    message = escape(
                        issue.get("message", issue.get("issue_text", ""))
                    )

                    location = issue.get("location", {})
                    line = issue.get(
                        "line_number",
                        location.get("row", "N/A"),
                    )

                    issue_rows.append(
                        "<tr>"
                        f"<td>{escape(category.title())}</td>"
                        f"<td>{code}</td>"
                        f"<td>{escape(line)}</td>"
                        f"<td>{message}</td>"
                        "</tr>"
                    )

            syntax = file_review.get("syntax", {})
            if syntax.get("status") != "passed":
                issue_rows.append(
                    "<tr>"
                    "<td>Syntax</td>"
                    "<td>N/A</td>"
                    "<td>N/A</td>"
                    f"<td>{escape(syntax.get('message', 'Syntax issue'))}</td>"
                    "</tr>"
                )

            rows = "".join(issue_rows)

            if not rows:
                rows = (
                    '<tr><td colspan="4">'
                    "No issues detected"
                    "</td></tr>"
                )

            sections.append(
                '<section class="file-card">'
                f"<h2>{filename}</h2>"
                f"<p>Status: <strong>{status}</strong></p>"
                "<table>"
                "<thead><tr>"
                "<th>Category</th><th>Code</th>"
                "<th>Line</th><th>Message</th>"
                "</tr></thead>"
                f"<tbody>{rows}</tbody>"
                "</table>"
                "</section>"
            )

        files_reviewed = escape(review.get("files_reviewed", len(reviews)))
        total_issues = escape(review.get("total_issues", 0))
        overall_status = escape(review.get("status", "unknown"))
        generated_at = escape(data.get("generated_at", "Unknown"))

        page = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>CodeGuard AI Report</title>
<style>
body {{
    margin: 0;
    background: #f4f6fb;
    color: #172033;
    font-family: Arial, sans-serif;
}}
header {{
    background: #18243c;
    color: white;
    padding: 32px;
}}
main {{
    max-width: 1100px;
    margin: 28px auto;
    padding: 0 18px;
}}
.summary {{
    display: flex;
    flex-wrap: wrap;
    gap: 16px;
    margin-bottom: 24px;
}}
.metric, .file-card {{
    background: white;
    padding: 22px;
    border-radius: 12px;
    box-shadow: 0 2px 12px #00000012;
}}
.metric {{
    flex: 1;
    min-width: 170px;
}}
.metric strong {{
    display: block;
    margin-top: 12px;
    font-size: 25px;
}}
.file-card {{
    margin-bottom: 20px;
    overflow-x: auto;
}}
table {{
    width: 100%;
    border-collapse: collapse;
}}
th, td {{
    padding: 12px;
    border-bottom: 1px solid #e5e9f0;
    text-align: left;
}}
th {{
    background: #eef2f9;
}}
footer {{
    text-align: center;
    padding: 24px;
    color: #667085;
}}
</style>
</head>
<body>
<header>
<h1>CodeGuard AI</h1>
<p>Automated Python Code Review Report</p>
</header>
<main>
<div class="summary">
<div class="metric">Files Reviewed<strong>{files_reviewed}</strong></div>
<div class="metric">Total Issues<strong>{total_issues}</strong></div>
<div class="metric">Overall Status<strong>{overall_status}</strong></div>
</div>
<p>Generated: {generated_at}</p>
{''.join(sections) or '<p>No changed files were reviewed.</p>'}
</main>
<footer>Generated locally by CodeGuard AI</footer>
</body>
</html>"""

        destination = Path(output_path)
        destination.parent.mkdir(parents=True, exist_ok=True)
        destination.write_text(page, encoding="utf-8")

        return {
            "status": "passed",
            "message": "HTML report generated successfully",
            "path": str(destination.resolve()),
        }

    except (OSError, ValueError, KeyError, TypeError) as error:
        return {
            "status": "error",
            "message": str(error),
        }
