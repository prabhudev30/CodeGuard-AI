import pytest
from pathlib import Path
from codeguard.upload_reviewer import review_uploaded_file, MAX_UPLOAD_BYTES


def test_valid_upload():
    result = review_uploaded_file("sample.py", b"import os\nprint(missing_name)\n")
    assert result["files_reviewed"] == 1
    assert result["total_issues"] >= 2
    assert result["reviews"][0]["file"] == "sample.py"


@pytest.mark.parametrize("name", ["", "invalid.txt", "file.py.txt"])
def test_invalid_filename(name):
    with pytest.raises(ValueError):
        review_uploaded_file(name, b"print(1)\n")


def test_oversized_upload():
    with pytest.raises(ValueError):
        review_uploaded_file("large.py", b"x" * (MAX_UPLOAD_BYTES + 1))


def test_non_bytes_upload():
    with pytest.raises(ValueError):
        review_uploaded_file("sample.py", "print(1)")


def test_windows_path_filename():
    result = review_uploaded_file("folder" + chr(92) + "sample.py", b"print(1)\n")
    assert result["reviews"][0]["file"] == "sample.py"


def test_temporary_files_cleaned(monkeypatch, tmp_path):
    import codeguard.upload_reviewer as module
    original = module.tempfile.TemporaryDirectory
    paths = []
    def tracked_directory(*args, **kwargs):
        directory = original(*args, dir=tmp_path, **kwargs)
        paths.append(Path(directory.name))
        return directory
    monkeypatch.setattr(module.tempfile, "TemporaryDirectory", tracked_directory)
    review_uploaded_file("sample.py", b"print(1)\n")
    assert paths and all(not path.exists() for path in paths)
