

from pathlib import Path

import streamlit as st

from codeguard.git_reviewer import review_changed_files
from codeguard.report_generator import save_json_report
from codeguard.html_report import generate_html_report


st.set_page_config(
    page_title="CodeGuard AI",
    page_icon="🛡️",
    layout="wide",
)

st.title("🛡️ CodeGuard AI")
st.caption("Local Python Code Quality & Security Dashboard")

st.info(
    "Review changed, tracked Python files in a local Git repository. "
    "Your source code is not executed or uploaded by CodeGuard AI."
)

project_path = st.text_input(
    "Git project folder",
    value=str(Path.cwd()),
)

if st.button("Run Code Review", type="primary"):
    folder = Path(project_path).expanduser()

    if not folder.is_dir():
        st.error("The selected folder does not exist.")
    else:
        with st.spinner("Analyzing Python files..."):
            result = review_changed_files(folder)

        if result["status"] == "error":
            st.error(result["message"])
        else:
            st.session_state["review_result"] = result
            st.success("Code review completed.")

if "review_result" in st.session_state:
    result = st.session_state["review_result"]

    st.subheader("Review Summary")

    col1, col2, col3 = st.columns(3)

    col1.metric("Files Reviewed", result["files_reviewed"])
    col2.metric("Total Issues", result["total_issues"])
    col3.metric("Status", result["status"])

    for review in result["reviews"]:
        with st.expander(
            f"{Path(review['file']).name} — {review['status']}",
            expanded=True,
        ):
            st.write("**File:**", review["file"])

            for category in ("syntax", "quality", "security"):
                details = review.get(category, {})

                st.markdown(f"**{category.title()}**")
                st.write(details.get("message", "No details"))

                
                issues = details.get("issues", [])

                if issues:
                    rows = []

                    for issue in issues:
                        location = issue.get("location") or {}

                        rows.append({
                            "Code": issue.get(
                                "code",
                                issue.get("test_id", "N/A"),
                            ),
                            "Severity": issue.get(
                                "severity",
                                issue.get("issue_severity", "N/A"),
                            ),
                            "Line": issue.get(
                                "line_number",
                                location.get("row", "N/A"),
                            ),
                            "Description": issue.get(
                                "message",
                                issue.get("issue_text", ""),
                            ),
                        })

                    st.dataframe(
                        rows,
                        width="stretch",
                        hide_index=True,
                    )


    if st.button("Generate Reports"):
        json_result = save_json_report(result)

        if json_result["status"] == "passed":
            html_result = generate_html_report()

            	
            if html_result["status"] == "passed":
                st.success("JSON and HTML reports generated.")

                json_path = Path(json_result["path"])
                html_path = Path(html_result["path"])

                st.code(str(json_path))
                st.code(str(html_path))

                col_json, col_html = st.columns(2)

                with col_json:
                    st.download_button(
                        label="Download JSON Report",
                        data=json_path.read_bytes(),
                        file_name="codeguard_report.json",
                        mime="application/json",
                    )

                with col_html:
                    st.download_button(
                        label="Download HTML Report",
                        data=html_path.read_bytes(),
                        file_name="codeguard_report.html",
                        mime="text/html",
                    )

            else:
                st.error(html_result["message"])
        else:
            st.error(json_result["message"])

