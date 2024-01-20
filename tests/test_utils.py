from http import HTTPStatus

import pytest

from mini_framework.responses import PlainTextResponse
from mini_framework.utils import (
    get_status_code_and_phrase,
    prepare_headers,
    prepare_kwargs,
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

    assert len(headers) == 2
    assert "text/plain" in headers["Content-Type"]
    assert headers["Content-Length"] == str(len(content))


def test_prepare_headers_with_response_with_headers() -> None:
    content = "Hello, World!"
    response = PlainTextResponse(content, headers={"X-Header": "Value"})

    headers = prepare_headers(response)

    assert len(headers) == 3
    assert "text/plain" in headers["Content-Type"]
    assert headers["Content-Length"] == str(len(content))
    assert headers["X-Header"] == "Value"


def test_prepare_kwargs_no_parameters() -> None:
    kwargs = {"a": 1, "b": 2}

    def callback() -> None:
        pass

    prepared_kwargs = prepare_kwargs(callback, kwargs)

    assert prepared_kwargs == {}


def test_prepare_kwargs_with_one_parameter() -> None:
    kwargs = {"a": 1, "b": 2}

    def callback(a: int) -> None:
        pass

    prepared_kwargs = prepare_kwargs(callback, kwargs)

    assert prepared_kwargs == {"a": 1}


def test_prepare_kwargs_with_unknown_parameter() -> None:
    kwargs = {"a": 1, "b": 2}

    def callback(c: int) -> None:
        pass

    prepared_kwargs = prepare_kwargs(callback, kwargs)

    assert prepared_kwargs == {}


def test_prepare_kwargs_with_kwargs_parameter() -> None:
    kwargs = {"a": 1, "b": 2}

    def callback(**kwargs) -> None:
        pass

    prepared_kwargs = prepare_kwargs(callback, kwargs)

    assert prepared_kwargs == kwargs
