
from pathlib import Path

import streamlit as st

from codeguard.git_reviewer import review_changed_files
from codeguard.upload_reviewer import review_uploaded_file
from codeguard.report_generator import save_json_report
from codeguard.html_report import generate_html_report
from codeguard.issue_formatter import format_issue, explain_issue, calculate_priority
from codeguard.issue_filter import filter_findings
from codeguard.syntax_findings import format_syntax_finding


# --------------------------------------------------
# Page configuration
# --------------------------------------------------

st.set_page_config(
    page_title="CodeGuard AI",
    page_icon="🛡️",
    layout="wide",
)

st.title("🛡️ CodeGuard AI")
st.caption("Local Python Code Quality & Security Dashboard")

st.info(
    "Review modified, staged, and newly created Python files "
    "in a local Git repository. "
    "Your source code is not executed or uploaded by CodeGuard AI."
)


review_mode = st.radio("Review Mode", ["Git Repository Review", "Upload Python File"], horizontal=True)
if st.session_state.get("previous_review_mode") != review_mode:
    for key in ("review_result", "review_folder", "json_report_path", "html_report_path"):
        st.session_state.pop(key, None)
    st.session_state["previous_review_mode"] = review_mode

if review_mode == "Upload Python File":
    uploaded = st.file_uploader("Choose a Python file", type=["py"], max_upload_size=2)
    if st.button("Review Uploaded File", type="primary"):
        if uploaded is None:
            st.warning("Choose a Python file first.")
        elif uploaded.size > 2 * 1024 * 1024:
            st.error("Maximum file size is 2 MB.")
        else:
            try:
                with st.spinner("Analyzing uploaded Python file..."):
                    result = review_uploaded_file(uploaded.name, uploaded.getvalue())
            except ValueError as error:
                st.session_state.pop("review_result", None)
                st.session_state.pop("json_report_path", None)
                st.session_state.pop("html_report_path", None)
                st.error(str(error))
                st.stop()
            if result["status"] == "error":
                st.session_state.pop("review_result", None)
                st.error("Uploaded file review failed.")
            else:
                st.session_state["review_result"] = result
                st.session_state.pop("json_report_path", None)
                st.session_state.pop("html_report_path", None)
                st.success("Uploaded file review completed.")

# --------------------------------------------------
# Project folder selection
# --------------------------------------------------

project_path = st.text_input(
    "Git project folder",
    value=str(Path.cwd()),
) if review_mode == "Git Repository Review" else None


# --------------------------------------------------
# Run code review
# --------------------------------------------------

if review_mode == "Git Repository Review" and st.button("Run Code Review", type="primary"):

    folder = Path(project_path).expanduser()

    if not folder.is_dir():
        st.error("The selected folder does not exist.")

    else:
        with st.spinner("Analyzing Python files..."):
            result = review_changed_files(folder)

        if result["status"] == "error":
            st.session_state.pop("review_result", None)
            st.error(result["message"])

        else:
            st.session_state["review_result"] = result
            st.session_state["review_folder"] = str(folder.resolve())
            st.success("Code review completed.")


# --------------------------------------------------
# Display review results
# --------------------------------------------------

if "review_result" in st.session_state:

    result = st.session_state["review_result"]

    st.subheader("Review Summary")

    col1, col2, col3 = st.columns(3)

    col1.metric(
        "Files Reviewed",
        result["files_reviewed"],
    )

    col2.metric(
        "Total Issues",
        result["total_issues"],
    )

    col3.metric(
        "Status",
        result["status"].replace("_", " ").title(),
    )

    st.subheader("Filter Findings")
    filter_col1, filter_col2, filter_col3 = st.columns(3)
    with filter_col1:
        selected_category = st.selectbox("Category", ["All", "Quality", "Security", "Syntax"])
    with filter_col2:
        selected_priority = st.selectbox("Priority", ["All", "High", "Medium", "Low", "Review"])
    with filter_col3:
        search_text = st.text_input("Search issues", placeholder="Rule, description, or filename")
    all_findings = []
    for file_review in result["reviews"]:
        syntax_finding = format_syntax_finding(file_review)
        if syntax_finding is not None:
            all_findings.append(syntax_finding)
        for category in ("quality", "security"):
            for issue in (file_review.get(category) or {}).get("issues", []):
                row = {**format_issue(issue, category), "Priority": calculate_priority(issue, category), **explain_issue(issue.get("test_id") or issue.get("code") or "N/A")}
                row["Category"] = category.title()
                row["File"] = file_review["file"]
                all_findings.append(row)
    visible_findings = filter_findings(all_findings, selected_category, selected_priority, search_text)
    st.caption(f"Showing {len(visible_findings)} of {len(all_findings)} findings")
    if visible_findings:
        st.dataframe(visible_findings, width="stretch", hide_index=True)
    elif all_findings:
        st.info("No findings match the selected filters.")

    # ----------------------------------------------
    # Individual file results
    # ----------------------------------------------

    for review in result["reviews"]:

        file_name = Path(review["file"]).name

        with st.expander(
            f"{file_name} — {review['status'].replace('_', ' ').title()}",
            expanded=False,
        ):

            st.write("**File:**", review["file"])

            for category in ("syntax", "quality", "security"):

                details = review.get(category, {})

                st.markdown(
                    f"**{category.title()}**"
                )

                st.write(
                    details.get("message", "No details")
                )

                issues = details.get("issues", [])

                if issues:

                    rows = [
                        {**format_issue(issue, category), "Priority": calculate_priority(issue, category), **explain_issue(issue.get("test_id") or issue.get("code") or "N/A")}
                        for issue in issues
                    ]

                    st.dataframe(
                        rows,
                        width="stretch",
                        hide_index=True,
                    )


    # ----------------------------------------------
    # Generate JSON and HTML reports
    # ----------------------------------------------

    if st.button("Generate Reports"):

        json_result = save_json_report(result)

        if json_result["status"] == "passed":

            html_result = generate_html_report()

            if html_result["status"] == "passed":

                st.success(
                    "JSON and HTML reports generated."
                )

                json_path = Path(json_result["path"])
                html_path = Path(html_result["path"])

                st.code(str(json_path))
                st.code(str(html_path))

                st.session_state["json_report_path"] = str(
                    json_path
                )

                st.session_state["html_report_path"] = str(
                    html_path
                )

            else:
                st.error(html_result["message"])

        else:
            st.error(json_result["message"])


    # ----------------------------------------------
    # Download generated reports
    # ----------------------------------------------

    json_report_path = st.session_state.get(
        "json_report_path"
    )

    html_report_path = st.session_state.get(
        "html_report_path"
    )

    if json_report_path and html_report_path:

        json_path = Path(json_report_path)
        html_path = Path(html_report_path)

        if json_path.is_file() and html_path.is_file():

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
