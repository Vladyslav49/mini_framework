import importlib
import sys
from contextlib import AbstractContextManager, nullcontext
from io import BytesIO
from typing import Callable
from unittest.mock import patch
from wsgiref.types import WSGIEnvironment

import pytest

import mini_framework.request
from mini_framework.request import (
    extract_headers,
    extract_path_params,
    extract_path_params_from_template,
    parse_query_params,
    Request,
    validate_path,
)
from mini_framework.responses import PlainTextResponse, prepare_headers
from mini_framework.utils import prepare_kwargs, prepare_path


def test_create_request() -> None:
    environ = {}
    path_params = {}

    Request(environ, path_params=path_params)


@pytest.mark.parametrize(
    "environ, expected_extracted_headers",
    [
        ({}, {}),
        ({"PATH_INFO": "/"}, {}),
        (
            {"HTTP_HOST": "localhost:8000", "HTTP_CONNECTION": "keep-alive"},
            {"Host": "localhost:8000", "Connection": "keep-alive"},
        ),
    ],
)
def test_extract_headers(
    environ: dict[str, str], expected_extracted_headers: dict[str, str]
) -> None:
    headers = extract_headers(environ)

    assert headers == expected_extracted_headers


@pytest.mark.parametrize(
    "path_template, path, expected_path_params, contextmanager",
    [
        (
            "/users/{user_id}/orders/{order_id}/",
            "/users/1/orders/2/",
            {"user_id": "1", "order_id": "2"},
            nullcontext(),
        ),
        (
            "/users/{user_id}/orders/{order_id}/items/",
            "/users/1/orders/2/",
            {},
            pytest.raises(ValueError, match="Expected 5 parts, got 4"),
        ),
        (
            "/users/{user_id}/orders/{order_id}/",
            "/users/1/orders/2/items/",
            {},
            pytest.raises(ValueError, match="Expected 4 parts, got 5"),
        ),
        (
            "/home/{id}/",
            "/users/1/",
            {},
            pytest.raises(ValueError, match="Expected 'home', got 'users'"),
        ),
        (
            "/",
            "/users/1/",
            {},
            nullcontext(),
        ),
    ],
)
def test_extract_path_params(
    path_template: str,
    path: str,
    expected_path_params: dict[str, str],
    contextmanager: AbstractContextManager,
) -> None:
    with contextmanager:
        params = extract_path_params(path_template, path)
        assert params == expected_path_params


@pytest.mark.parametrize(
    "path, expected_path_params, contextmanager",
    [
        (
            "/users/",
            [],
            nullcontext(),
        ),
        (
            "/users/{user_id}/orders/{order_id}/",
            ["user_id", "order_id"],
            nullcontext(),
        ),
        (
            "/users/{user_id}/orders/{user_id}/",
            [],
            pytest.raises(ValueError, match="Parameters must be unique"),
        ),
        (
            "/users/{user-id}/",
            [],
            pytest.raises(
                ValueError,
                match="Parameter name 'user-id' is not a valid Python identifier",  # noqa: E501
            ),
        ),
        (
            "/users/{class}/",
            [],
            pytest.raises(
                ValueError, match="Parameter name 'class' is a Python keyword"
            ),
        ),
        (
            "/users/{{user_id}/",
            [],
            pytest.raises(ValueError, match="Invalid path"),
        ),
    ],
)
def test_extract_path_params_from_template(
    path: str,
    expected_path_params: list[str],
    contextmanager: AbstractContextManager,
) -> None:
    with contextmanager:
        params = extract_path_params_from_template(path)
        assert params == expected_path_params


@pytest.mark.parametrize(
    "headers, expected_prepared_headers",
    [
        (
            {},
            [
                ("Content-Type", "text/plain; charset=utf-8"),
                ("Content-Length", "13"),
            ],
        ),
        (
            {"X-Header": "Value"},
            [
                ("X-Header", "Value"),
                ("Content-Type", "text/plain; charset=utf-8"),
                ("Content-Length", "13"),
            ],
        ),
    ],
)
def test_prepare_headers(
    headers: dict[str, str], expected_prepared_headers: list[tuple[str, str]]
) -> None:
    response = PlainTextResponse(
        "Hello, World!", charset="utf-8", headers=headers
    )

    prepared_headers = prepare_headers(response)

    assert prepared_headers == expected_prepared_headers


def test_prepare_headers_with_cookies() -> None:
    content = "Hello, World!"
    response = PlainTextResponse(content)
    response.set_cookie("name", "john")
    response.set_cookie("age", "20")

    headers = prepare_headers(response)

    assert headers[0][1] == "name=john; Path=/; SameSite=lax"
    assert headers[1][1] == "age=20; Path=/; SameSite=lax"


@pytest.mark.parametrize(
    "callback, expected_prepared_kwargs",
    [
        (lambda: None, {}),
        (lambda a: None, {"a": 1}),
        (lambda c: None, {}),
        (lambda **kwargs: None, {"a": 1, "b": 2}),
    ],
)
def test_prepare_kwargs(
    callback: Callable[..., None], expected_prepared_kwargs: dict[str, str]
) -> None:
    kwargs = {"a": 1, "b": 2}

    prepared_kwargs = prepare_kwargs(callback, kwargs)

    assert prepared_kwargs == expected_prepared_kwargs


@pytest.mark.parametrize("path", ["/home/", "/home"])
def test_prepare_path(path: str) -> None:
    assert prepare_path(path) == "/home/"


@pytest.mark.parametrize(
    "environ, expected_query_params",
    [
        ({}, {}),
        ({"QUERY_STRING": ""}, {}),
        (
            {"QUERY_STRING": "foo=bar&baz=qux&baz=quux&corge="},
            {
                "foo": ["bar"],
                "baz": ["qux", "quux"],
                "corge": [""],
            },
        ),
    ],
)
def test_parse_query_params(
    environ: WSGIEnvironment, expected_query_params: dict[str, str | list[str]]
) -> None:
    query_params = parse_query_params(environ)

    assert query_params == expected_query_params


@pytest.mark.parametrize(
    "path, params, contextmanager",
    [
        ("/home/{id}", ["id"], nullcontext()),
        (
            "/home/{{id}}/",
            ["id"],
            pytest.raises(ValueError, match="Invalid path"),
        ),
        ("/home/{id}/", [], pytest.raises(KeyError)),
    ],
)
def test_validate_path(
    path: str, params: list[str], contextmanager: AbstractContextManager
) -> None:
    with contextmanager:
        validate_path(path, params)


def test_form() -> None:
    environ = {
        "wsgi.input": BytesIO(b"a=1&b=2"),
        "HTTP_CONTENT_TYPE": "application/x-www-form-urlencoded",
    }

    path_params = {}

    request = Request(environ, path_params=path_params)

    form = request.form()

    assert form.fields[0].field_name == b"a"
    assert form.fields[0].value == b"1"
    assert form.fields[1].field_name == b"b"
    assert form.fields[1].value == b"2"


def test_form_when_multipart_is_not_installed() -> None:
    environ = {}
    path_params = {}

    request = Request(environ, path_params=path_params)

    with patch.dict(sys.modules, {"multipart": None}):
        importlib.reload(mini_framework.request)
        with pytest.raises(
            AssertionError, match="python-multipart is not installed"
        ):
            request.form()

    importlib.reload(mini_framework.request)
