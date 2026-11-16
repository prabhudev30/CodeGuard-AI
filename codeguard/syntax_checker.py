
import ast
from pathlib import Path


def check_syntax(file_path):
    """Check Python syntax without executing the file."""

    path = Path(file_path)

    if not path.is_file():
        return {
            "status": "error",
            "message": "File does not exist",
        }

    try:
        source = path.read_text(encoding="utf-8-sig")
        ast.parse(source, filename=str(path))

        return {
            "status": "passed",
            "message": "No Python syntax errors found",
        }

    except SyntaxError as error:
        return {
            "status": "failed",
            "message": error.msg,
            "line": error.lineno,
            "column": error.offset,
        }

    except (OSError, UnicodeError, ValueError) as error:
        return {
            "status": "error",
            "message": f"Unable to read file: {error}",
        }
