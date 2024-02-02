import itertools
from contextlib import AbstractContextManager, nullcontext
from http import HTTPStatus
from unittest.mock import Mock

import pytest

from mini_framework import Application, Response
from mini_framework.exceptions import HTTPException
from mini_framework.responses import (
    get_status_code_and_phrase,
    PlainTextResponse,
)


@pytest.mark.parametrize(
    "content, expected_body",
    [
        (None, b""),
        ("hi", b"hi"),
    ],
)
def test_create_response(content: str, expected_body: bytes) -> None:
    response = Response(content=content)

    assert response.body == expected_body


def test_status_code(app: Application, mock_request: Mock) -> None:
    @app.get("/")
    def index():
        return PlainTextResponse(
            "Hello, World!", status_code=HTTPStatus.IM_A_TEAPOT
        )

    response = app.propagate(mock_request)

    assert response.status_code == HTTPStatus.IM_A_TEAPOT


def test_http_exception(app: Application, mock_request: Mock) -> None:
    @app.get("/")
    def index():
        raise HTTPException(status_code=HTTPStatus.IM_A_TEAPOT)

    response = app.propagate(mock_request)

    assert response.status_code == HTTPStatus.IM_A_TEAPOT
    assert response.body == HTTPStatus.IM_A_TEAPOT.phrase.encode()


def test_http_exception_with_detail(
    app: Application, mock_request: Mock
) -> None:
    @app.get("/")
    def index():
        raise HTTPException(
            status_code=HTTPStatus.IM_A_TEAPOT,
            detail="I'm a teapot with detail",
        )

    response = app.propagate(mock_request)

    assert response.status_code == HTTPStatus.IM_A_TEAPOT
    assert response.body == "I'm a teapot with detail".encode()


def test_http_exception_with_headers(
    app: Application, mock_request: Mock
) -> None:
    @app.get("/")
    def index():
        raise HTTPException(
            status_code=HTTPStatus.IM_A_TEAPOT, headers={"X-Header": "Value"}
        )

    response = app.propagate(mock_request)

    assert response.status_code == HTTPStatus.IM_A_TEAPOT
    assert response.body == HTTPStatus.IM_A_TEAPOT.phrase.encode()
    assert response.headers["X-Header"] == "Value"


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
