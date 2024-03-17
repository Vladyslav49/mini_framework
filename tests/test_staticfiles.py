import re
from pathlib import Path
from unittest.mock import Mock, create_autospec

import pytest

from mini_framework import Request, Application
from mini_framework.responses import FileResponse
from mini_framework.staticfiles import is_not_modified
from mini_framework.router import NOT_FOUND_RESPONSE


def test_create_staticfiles_with_existing_directory(
    app: Application, tmp_path: Path
) -> None:
    directory = tmp_path / "directory"
    directory.mkdir()

    app.add_staticfiles("/static/", directory)


def test_create_staticfiles_with_nonexistent_directory(
    app: Application, tmp_path: Path
) -> None:
    directory = tmp_path / "directory"

    with pytest.raises(
        NotADirectoryError,
        match=re.escape(
            f"Directory '{directory}' does not exist or is not a directory"
        ),
    ):
        app.add_staticfiles("/static/", directory)


def test_create_staticfiles_with_file_instead_of_directory(
    app: Application, tmp_path: Path
) -> None:
    file = tmp_path / "directory"
    file.touch()

    with pytest.raises(
        NotADirectoryError,
        match=re.escape(
            f"Directory '{file}' does not exist or is not a directory"
        ),
    ):
        app.add_staticfiles("/static/", file)


def test_etag_match(mocked_request: Mock) -> None:
    mocked_request.headers = {"if-none-match": "123456"}
    mocked_response = create_autospec(Request, headers={"etag": "123456"})

    assert is_not_modified(mocked_request, mocked_response)


def test_etag_not_match(mocked_request: Mock) -> None:
    mocked_request.headers = {"if-none-match": "123456"}
    mocked_response = create_autospec(Request, headers={"etag": "654321"})

    assert not is_not_modified(mocked_request, mocked_response)


def test_if_modified_since_not_modified(mocked_request: Mock) -> None:
    mocked_request.headers = {
        "if-modified-since": "Sat, 13 Mar 2021 15:00:00 GMT"
    }
    mocked_response = create_autospec(
        Request, headers={"last-modified": "Sat, 13 Mar 2021 14:00:00 GMT"}
    )

    assert is_not_modified(mocked_request, mocked_response)


def test_if_modified_since_modified(mocked_request: Mock) -> None:
    mocked_request.headers = {
        "if-modified-since": "Sat, 13 Mar 2021 15:00:00 GMT"
    }
    mocked_response = create_autospec(
        Request, headers={"last-modified": "Sat, 13 Mar 2021 16:00:00 GMT"}
    )

    assert not is_not_modified(mocked_request, mocked_response)


def test_callback_file_found(
    app: Application, mocked_request: Mock, tmp_path: Path
) -> None:
    path = "styles.css"
    directory = tmp_path / "directory"
    directory.mkdir()
    file = directory / path
    file.touch()
    app.add_staticfiles("/static/", directory)
    mocked_request.path = f"/static/{path}/"
    mocked_request.path_params = {"path": path}
    mocked_request.headers = {}

    response = app.propagate(mocked_request)

    assert isinstance(response, FileResponse)
    assert response.path == file


def test_callback_file_not_found(
    app: Application, mocked_request: Mock, tmp_path: Path
) -> None:
    path = "styles.css"
    directory = tmp_path / "directory"
    directory.mkdir()
    app.add_staticfiles("/static/", directory)
    mocked_request.path = f"/static/{path}/"
    mocked_request.path_params = {"path": path}

    response = app.propagate(mocked_request)

    assert response is NOT_FOUND_RESPONSE
