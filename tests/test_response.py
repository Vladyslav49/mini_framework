from http import HTTPMethod, HTTPStatus
from unittest.mock import Mock

import pytest

from mini_framework import Application
from mini_framework.responses import (
    get_status_code_and_phrase,
    PlainTextResponse,
    prepare_headers,
)


@pytest.mark.parametrize("status", list(HTTPStatus))
def test_get_status_code_and_phrase(status: HTTPStatus) -> None:
    assert get_status_code_and_phrase(status) == f"{status} {status.phrase}"


def test_get_status_code_and_phrase_with_invalid_status_code() -> None:
    with pytest.raises(ValueError, match="Invalid status code: 999"):
        get_status_code_and_phrase(999)


def test_prepare_headers_with_response_without_headers() -> None:
    content = "Hello, World!"
    response = PlainTextResponse(content)

    headers = prepare_headers(response)

    headers = dict(headers)

    assert len(headers) == 2
    assert "text/plain" in headers["Content-Type"]
    assert headers["Content-Length"] == str(len(content))


def test_prepare_headers_with_response_with_headers() -> None:
    content = "Hello, World!"
    response = PlainTextResponse(content, headers={"X-Header": "Value"})

    headers = prepare_headers(response)

    headers = dict(headers)

    assert len(headers) == 3
    assert "text/plain" in headers["Content-Type"]
    assert headers["Content-Length"] == str(len(content))
    assert headers["X-Header"] == "Value"


def test_prepare_headers_with_cookies() -> None:
    content = "Hello, World!"
    response = PlainTextResponse(content)

    response.set_cookie("name", "john")
    response.set_cookie("age", "20")

    headers = prepare_headers(response)

    assert headers[0][1] == "name=john; Path=/; SameSite=lax"
    assert headers[1][1] == "age=20; Path=/; SameSite=lax"


def test_status_code_in_response(app: Application) -> None:
    @app.get("/")
    def index():
        return PlainTextResponse(
            "Hello, World!", status_code=HTTPStatus.IM_A_TEAPOT
        )

    request = Mock()
    request.path = "/"
    request.method = HTTPMethod.GET

    response = app.propagate(request)

    assert response.status_code == HTTPStatus.IM_A_TEAPOT
