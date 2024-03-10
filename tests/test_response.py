import itertools
from contextlib import AbstractContextManager, nullcontext
from datetime import datetime, timedelta, UTC
from email.utils import format_datetime
from http import HTTPStatus
from pathlib import Path
from unittest.mock import Mock

import pytest

from mini_framework import Application, Response
from mini_framework.exceptions import HTTPException
from mini_framework.responses import (
    get_status_code_and_phrase,
    PlainTextResponse,
    FileResponse,
)


@pytest.mark.parametrize(
    "content, expected_rendered_response",
    [
        (None, b""),
        ("hi", b"hi"),
        (b"hi", b"hi"),
    ],
)
def test_render_response(
    content: str, expected_rendered_response: bytes
) -> None:
    response = Response(content=content)

    assert response.render() == expected_rendered_response


def test_status_code(app: Application, mocked_request: Mock) -> None:
    @app.get("/")
    def index():
        return PlainTextResponse(
            "Hello, World!", status_code=HTTPStatus.IM_A_TEAPOT
        )

    response = app.propagate(mocked_request)

    assert response.status_code == HTTPStatus.IM_A_TEAPOT


def test_http_exception(app: Application, mocked_request: Mock) -> None:
    @app.get("/")
    def index():
        raise HTTPException(status_code=HTTPStatus.IM_A_TEAPOT)

    response = app.propagate(mocked_request)

    assert response.status_code == HTTPStatus.IM_A_TEAPOT
    assert response.content == {"detail": HTTPStatus.IM_A_TEAPOT.phrase}


def test_http_exception_with_detail(
    app: Application, mocked_request: Mock
) -> None:
    @app.get("/")
    def index():
        raise HTTPException(
            status_code=HTTPStatus.IM_A_TEAPOT,
            detail="I'm a teapot with detail",
        )

    response = app.propagate(mocked_request)

    assert response.status_code == HTTPStatus.IM_A_TEAPOT
    assert response.content == {"detail": "I'm a teapot with detail"}


def test_http_exception_with_headers(
    app: Application, mocked_request: Mock
) -> None:
    @app.get("/")
    def index():
        raise HTTPException(
            status_code=HTTPStatus.IM_A_TEAPOT, headers={"X-Header": "Value"}
        )

    response = app.propagate(mocked_request)

    assert response.status_code == HTTPStatus.IM_A_TEAPOT
    assert response.content == {"detail": HTTPStatus.IM_A_TEAPOT.phrase}
    assert response.headers["X-Header"] == "Value"


def test_create_http_exception_with_invalid_status_code(
    app: Application, mocked_request: Mock
) -> None:
    with pytest.raises(ValueError, match="Invalid status code: 999"):
        HTTPException(status_code=999)


@pytest.mark.parametrize(
    "status, contextmanager",
    [
        *itertools.zip_longest(list(HTTPStatus), [], fillvalue=nullcontext()),
        (999, pytest.raises(ValueError, match="Invalid status code: 999")),
    ],
)
def test_get_status_code_and_phrase(
    status: HTTPStatus, contextmanager: AbstractContextManager
) -> None:
    with contextmanager:
        assert (
            get_status_code_and_phrase(status) == f"{status} {status.phrase}"
        )


@pytest.fixture()
def file(tmp_path: Path) -> Path:
    file = tmp_path / "file.txt"
    file.touch()
    return file


def test_valid_file_response(file: Path) -> None:
    file.write_text("Hello, World!")
    response = FileResponse(file)

    assert response.path == file
    assert response.headers["Content-Length"] == "13"
    assert (
        response.headers["Content-Disposition"]
        == 'attachment; filename="file.txt"'
    )


def test_file_not_found() -> None:
    with pytest.raises(
        FileNotFoundError, match="File 'nonexistent_file.txt' not found"
    ):
        FileResponse("nonexistent_file.txt")


def test_invalid_file_path(tmp_path: Path) -> None:
    directory = tmp_path / "directory"
    directory.mkdir()

    with pytest.raises(
        ValueError, match=f"'{directory}' is not a valid file path"
    ):
        FileResponse(directory)


def test_custom_filename(file: Path) -> None:
    response = FileResponse(file, filename="custom_name.txt")

    assert response.filename == "custom_name.txt"
    assert (
        'filename="custom_name.txt"' in response.headers["Content-Disposition"]
    )


def test_stat_headers(file: Path) -> None:
    mocked_stat_result = Mock()
    mocked_stat_result.st_size = 13
    mocked_stat_result.st_mtime = 1234567890
    response = FileResponse(file, stat_result=mocked_stat_result)

    assert response.stat_result == mocked_stat_result
    assert response.headers["Content-Length"] == "13"
    assert response.headers["Last-Modified"] == "Fri, 13 Feb 2009 23:31:30 GMT"
    assert "Etag" in response.headers


def test_iter_content(file: Path) -> None:
    file.write_text("Hello, World!")
    response = FileResponse(file)
    content = b"".join(response.iter_content())

    assert content == b"Hello, World!"


def test_set_cookie_with_expires() -> None:
    response = Response(content=None)
    expires = datetime.now(UTC) + timedelta(hours=1)

    response.set_cookie("name", "John", expires=expires)

    expires_gmt = format_datetime(expires, usegmt=True)

    expected_cookie = f"name=John; expires={expires_gmt}; Path=/; SameSite=lax"

    assert response.headers["Set-Cookie"] == expected_cookie


def test_set_cookie_with_domain() -> None:
    response = Response(content=None)
    domain = "example.com"

    response.set_cookie("name", "John", domain=domain)

    expected_cookie = f"name=John; Domain={domain}; Path=/; SameSite=lax"

    assert response.headers["Set-Cookie"] == expected_cookie


def test_set_cookie_with_secure() -> None:
    response = Response(content=None)

    response.set_cookie("name", "John", secure=True)

    expected_cookie = "name=John; Path=/; SameSite=lax; Secure"

    assert response.headers["Set-Cookie"] == expected_cookie
