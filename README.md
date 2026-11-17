# CodeGuard AI

CodeGuard AI is a free, local Python code-review dashboard built with Streamlit. It helps developers inspect changed Python files for syntax errors, code-quality problems, and potential security vulnerabilities.

## Features

- Python syntax checking using the built-in AST parser.
- Code-quality analysis using Ruff.
- Security scanning using Bandit.
- Git integration to review modified, staged, and untracked Python files.
- Dashboard filters for category, priority, and keyword.
- Explanations and suggested fixes for supported findings.
- Downloadable JSON and HTML reports.
- Local processing without paid AI APIs.

## Requirements

- Python 3.12 or a compatible Python version.
- Git installed and available in PATH.
- Windows CMD for the commands below.

## Installation

1. Open CMD in the CodeGuard-AI project directory.
2. Create a virtual environment: `python -m venv .venv`
3. Activate it: `.venv\Scripts\activate`
4. Install dependencies: `python -m pip install -r requirements.txt`

## Launch the dashboard

Run: `python -m streamlit run dashboard.py`

Open `http://localhost:8501` in your browser.

## Review Python code

1. Enter the path of a local Git repository.
2. Select Run Code Review.
3. Inspect syntax, quality, and security findings.
4. Use category, priority, and search filters to narrow results.
5. Expand individual file sections for additional details.

## Export reports

Use Generate Reports to create JSON and HTML reports. Download the generated reports using the dashboard controls.

## Run automated tests

Run: `python -m pytest tests -q`

## Security and limitations

CodeGuard AI analyzes local source files without intentionally executing the reviewed Python code. Ruff and Bandit are static-analysis tools; their findings may include false positives or miss vulnerabilities. Review suggestions before applying changes. Do not treat a clean report as a security guarantee.

## Project status

Version 1.4 development on the develop-v1.4 branch.
