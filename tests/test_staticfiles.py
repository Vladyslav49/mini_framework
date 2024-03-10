from pathlib import Path
from unittest.mock import Mock, create_autospec

import pytest

from mini_framework import Request
from mini_framework.responses import FileResponse
from mini_framework.staticfiles import (
    StaticFiles,
    _is_not_modified,
    NOT_FOUND_RESPONSE,
)


def test_create_staticfiles_with_existing_directory(tmp_path: Path) -> None:
    directory = tmp_path / "directory"
    directory.mkdir()

    StaticFiles(directory=directory)


def test_create_staticfiles_with_nonexistent_directory(tmp_path: Path) -> None:
    directory = tmp_path / "directory"

    with pytest.raises(
        NotADirectoryError,
        match=f"Directory {str(directory)!r} does not exist or is not a directory",
    ):
        StaticFiles(directory=directory)


def test_create_staticfiles_with_file_instead_of_directory(
    tmp_path: Path,
) -> None:
    file = tmp_path / "directory"
    file.touch()

    with pytest.raises(
        NotADirectoryError,
        match=f"Directory {str(file)!r} does not exist or is not a directory",
    ):
        StaticFiles(directory=file)


def test_etag_match(mocked_request: Mock) -> None:
    mocked_request.headers = {"if-none-match": "123456"}
    mocked_response = create_autospec(Request, headers={"etag": "123456"})

    assert _is_not_modified(mocked_request, mocked_response)


def test_etag_not_match(mocked_request: Mock) -> None:
    mocked_request.headers = {"if-none-match": "123456"}
    mocked_response = create_autospec(Request, headers={"etag": "654321"})

    assert not _is_not_modified(mocked_request, mocked_response)


def test_if_modified_since_not_modified(mocked_request: Mock) -> None:
    mocked_request.headers = {
        "if-modified-since": "Sat, 13 Mar 2021 15:00:00 GMT"
    }
    mocked_response = create_autospec(
        Request, headers={"last-modified": "Sat, 13 Mar 2021 14:00:00 GMT"}
    )

    assert _is_not_modified(mocked_request, mocked_response)


def test_if_modified_since_modified(mocked_request: Mock) -> None:
    mocked_request.headers = {
        "if-modified-since": "Sat, 13 Mar 2021 15:00:00 GMT"
    }
    mocked_response = create_autospec(
        Request, headers={"last-modified": "Sat, 13 Mar 2021 16:00:00 GMT"}
    )

    assert not _is_not_modified(mocked_request, mocked_response)


def test_callback_file_found(mocked_request: Mock, tmp_path: Path) -> None:
    path = "styles.css"
    directory = tmp_path / "directory"
    directory.mkdir()
    file = directory / path
    file.touch()
    staticfiles = StaticFiles(directory=directory)
    mocked_request.headers = {}

    response = staticfiles.callback(mocked_request, path)

    assert isinstance(response, FileResponse)
    assert response.path == file


def test_callback_file_not_found(mocked_request: Mock, tmp_path: Path) -> None:
    path = "styles.css"
    directory = tmp_path / "directory"
    directory.mkdir()
    staticfiles = StaticFiles(directory=directory)

    response = staticfiles.callback(mocked_request, path)

    assert response is NOT_FOUND_RESPONSE
