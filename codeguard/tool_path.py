import shutil
from pathlib import Path


def resolve_executable(name):
    """Return an absolute path to a local executable, if one is available."""

    found = shutil.which(name)

    if not found:
        return None

    path = Path(found)

    if not path.is_absolute() or not path.is_file():
        return None

    return path
