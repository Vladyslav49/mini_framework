import pytest

from mini_framework.request import (
    extract_headers,
    extract_path_params,
    extract_path_params_from_template,
    parse_query_params,
)


def test_parse_query_params() -> None:
    environ = {"QUERY_STRING": "foo=bar&baz=qux&baz=quux&corge="}

    query_params = parse_query_params(environ)

    assert query_params == {
        "foo": "bar",
        "baz": ["qux", "quux"],
        "corge": "",
    }


def test_parse_query_params_empty() -> None:
    environ = {"QUERY_STRING": ""}

    query_params = parse_query_params(environ)

    assert query_params == {}


def test_parse_query_params_no_query_string() -> None:
    environ = {}

    query_params = parse_query_params(environ)

    assert query_params == {}


def test_extract_headers() -> None:
    environ = {
        "HTTP_HOST": "localhost:8000",
        "HTTP_ACCEPT_ENCODING": "gzip, deflate",
        "HTTP_CONNECTION": "keep-alive",
    }

    headers = extract_headers(environ)

    assert headers == {
        "Host": "localhost:8000",
        "Accept-Encoding": "gzip, deflate",
        "Connection": "keep-alive",
    }


def test_extract_headers_empty() -> None:
    environ = {}

    headers = extract_headers(environ)

    assert headers == {}


def test_extract_path_params_from_template() -> None:
    path = "/users/{user_id}/orders/{order_id}"

    params = extract_path_params_from_template(path)

    assert params == ["user_id", "order_id"]


def test_extract_path_params_from_template_without_params() -> None:
    path = "/users/"

    params = extract_path_params_from_template(path)

    assert params == []


def test_extract_path_params_from_template_with_no_uniqueness() -> None:
    path = "/users/{user_id}/orders/{user_id}"

    with pytest.raises(
        ValueError, match=f"Invalid path: {path!r}. Parameters must be unique"
    ):
        extract_path_params_from_template(path)


def test_extract_path_params_from_template_with_invalid_identifier() -> None:
    path = "/users/{user-id}"

    with pytest.raises(
        ValueError,
        match=f"Invalid path: {path!r}. Parameter name 'user-id' is not a valid Python identifier",  # noqa: E501
    ):
        extract_path_params_from_template(path)


def test_extract_path_params_from_template_with_keyword() -> None:
    path = "/users/{class}"

    with pytest.raises(
        ValueError,
        match=f"Invalid path: {path!r}. Parameter name 'class' is a Python keyword",  # noqa: E501
    ):
        extract_path_params_from_template(path)


def test_extract_path_params_from_template_with_invalid_path() -> None:
    path = "/users/{{user_id}/"

    with pytest.raises(ValueError, match=f"Invalid path: {path!r}."):
        extract_path_params_from_template(path)


def test_extract_path_params() -> None:
    path_template = "/users/{user_id}/orders/{order_id}"
    path = "/users/1/orders/2"

    params = extract_path_params(path_template, path)

    assert params == {"user_id": "1", "order_id": "2"}


def test_extract_path_params_wrong_number_of_parts() -> None:
    path_template = "/users/{user_id}/orders/{order_id}/"
    path = "/users/1/orders/2/extra/"

    with pytest.raises(
        ValueError,
        match=f"Invalid path: {path!r}. Expected 4 parts, got 5",
    ):
        extract_path_params(path_template, path)


def test_extract_path_params_with_invalid_path() -> None:
    path_template = "/home/{id}/"
    path = "/users/1/"

    with pytest.raises(
        ValueError,
        match=f"Invalid path: {path!r}. Expected 'home', got 'users'",
    ):
        extract_path_params(path_template, path)
