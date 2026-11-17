# CodeGuard AI

CodeGuard AI is a free, local Python code-review dashboard built with Streamlit. It helps developers inspect Python files for syntax errors, code-quality problems, and potential security vulnerabilities.

## Features

- Python syntax checking using the built-in AST parser.
- Code-quality analysis using Ruff.
- Security scanning using Bandit.
- Git integration to review modified, staged, and untracked Python files.
- Python file upload and review.
- Dashboard filters for category, priority, and keyword.
- Code-health scores for quality, security, syntax, and overall health.
- Offline Smart Fix Assistant with rule-based explanations and suggested fixes.
- Illustrative before-and-after code examples for supported findings.
- Downloadable JSON and HTML reports.
- Local processing without paid AI APIs.

## Requirements

- Python 3.12 or a compatible Python version.
- Git installed and available in PATH for repository review.
- Windows CMD for the commands below.

## Installation

1. Open CMD in the CodeGuard-AI project directory.
2. Create a virtual environment: `python -m venv .venv`
3. Activate it: `.venv\Scripts\activate`
4. Install dependencies: `python -m pip install -r requirements.txt`

## Launch the Dashboard

Run:

`python -m streamlit run dashboard.py`

Open `http://localhost:8501` in your browser.

## Review Python Code

### Option 1: Git Repository Review

1. Enter the path of a local Git repository.
2. Select Run Code Review.
3. Inspect syntax, quality, and security findings.
4. Use category, priority, and search filters to narrow results.
5. Expand individual file sections for additional details.

### Option 2: Upload Python Files

1. Select Upload Python Files.
2. Upload supported `.py` files.
3. Run the review.
4. Inspect the detected issues and code-health scores.
5. Review the available suggestions and examples.

## Offline Smart Fix Assistant

The Offline Smart Fix Assistant provides:

- Explanations of supported Python code-quality and security findings.
- Reasons why detected issues matter.
- Suggested corrections.
- Illustrative before-and-after Python examples.

The assistant uses predefined rules and does not require a cloud-based generative AI model.

Suggested corrections must be reviewed and applied manually.

## Export Reports

Use Generate Reports to create JSON and HTML reports. Download the generated reports using the dashboard controls.

## Run Automated Tests

Run:

`python -m pytest tests -q`

## Offline Usage

CodeGuard AI runs locally using Python and Streamlit.

Once Python and the required dependencies are installed, the core code-review features can operate without an internet connection.

Start the dashboard:

`python -m streamlit run dashboard.py`

Then open:

`http://localhost:8501`

Core analysis is performed using locally installed tools.

## Security and Limitations

- CodeGuard AI analyzes local source files without intentionally executing the reviewed Python code.
- Ruff and Bandit are static-analysis tools; findings may include false positives or miss vulnerabilities.
- A clean report does not guarantee that code is secure or bug-free.
- Suggested fixes are illustrative and should be reviewed manually.
- The application does not automatically modify reviewed source files.
- Performance depends on project size and available system resources.

## Project Status

**Version 1.5.0 — Offline Smart Fix Assistant**

The v1.5.0 release includes Python code-quality analysis, security scanning, syntax checking, Git repository review, Python file uploads, code-health scoring, offline fix guidance, and HTML/JSON reporting.

The application is intended for local development and educational code review. Public deployment and production-scale performance have not been validated.