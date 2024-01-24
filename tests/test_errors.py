from http import HTTPMethod, HTTPStatus
from typing import Any
from unittest.mock import Mock

import pytest

from mini_framework import Application
from mini_framework.exceptions import HTTPException
from mini_framework.filters.exception import (
    ExceptionTypeFilter,
    HTTPExceptionStatusCodeFilter,
)
from mini_framework.middlewares.base import CallNext
from mini_framework.responses import PlainTextResponse
from mini_framework.routes.manager import SkipRoute


def test_error_is_alias_for_errors(app: Application) -> None:
    assert app.error is app.errors


def test_error(app: Application) -> None:
    @app.get("/")
    def index():
        raise Exception

    @app.error()
    def error(exception: Exception):
        return PlainTextResponse("Error")

    request = Mock()
    request.path = "/"
    request.method = HTTPMethod.GET

    response = app.propagate(request)

    assert response.body == "Error".encode()


def test_multiple_errors(app: Application) -> None:
    @app.get("/")
    def index():
        raise Exception

    @app.error()
    def error(exception: Exception):
        return PlainTextResponse("Error")

    @app.error()
    def error2(exception: Exception):
        assert False  # noqa: B011

    request = Mock()
    request.path = "/"
    request.method = HTTPMethod.GET

    response = app.propagate(request)

    assert response.body == "Error".encode()


def test_error_type(app: Application) -> None:
    @app.get("/")
    def index():
        raise IndexError

    @app.error()
    def error(exception: Exception):
        assert isinstance(exception, IndexError)
        return PlainTextResponse("Error")

    request = Mock()
    request.path = "/"
    request.method = HTTPMethod.GET

    app.propagate(request)


def test_do_not_handle_error(app: Application) -> None:
    @app.get("/")
    def index():
        raise Exception("Error in index")

    @app.error(ExceptionTypeFilter(IndexError))
    def error(exception: Exception):
        assert False  # noqa: B011

    request = Mock()
    request.path = "/"
    request.method = HTTPMethod.GET

    with pytest.raises(Exception, match="Error in index"):
        app.propagate(request)


def test_handle_error_by_type(app: Application) -> None:
    @app.get("/")
    def index():
        raise IndexError

    @app.error(ExceptionTypeFilter(IndexError))
    def error(exception: Exception):
        return PlainTextResponse("Error")

    request = Mock()
    request.path = "/"
    request.method = HTTPMethod.GET

    response = app.propagate(request)

    assert response.body == "Error".encode()


def test_error_with_root_filter(app: Application) -> None:
    app.error.filter(ExceptionTypeFilter(IndexError))

    @app.get("/")
    def index():
        raise Exception("Error in index")

    @app.error()
    def error(exception: Exception):
        assert False  # noqa: B011

    request = Mock()
    request.path = "/"
    request.method = HTTPMethod.GET

    with pytest.raises(Exception, match="Error in index"):
        app.propagate(request)


def test_error_middleware(app: Application) -> None:
    @app.get("/")
    def index():
        raise IndexError

    @app.error.middleware
    def middleware(call_next: CallNext, data: dict[str, Any]) -> Any:
        exception: Exception = data["exception"]
        assert isinstance(exception, IndexError)
        data["middleware_data"] = "middleware_data"
        return call_next(data)

    @app.error()
    def error(exception: Exception, middleware_data: str):
        assert middleware_data == "middleware_data"
        return PlainTextResponse("Error")

    request = Mock()
    request.path = "/"
    request.method = HTTPMethod.GET

    response = app.propagate(request)

    assert response.body == "Error".encode()


def test_error_outer_middleware(app: Application) -> None:
    @app.get("/")
    def index():
        raise IndexError

    @app.error.outer_middleware
    def middleware(call_next: CallNext, data: dict[str, Any]) -> Any:
        exception: Exception = data["exception"]
        assert isinstance(exception, IndexError)
        data["outer_middleware_data"] = "outer_middleware_data"
        return call_next(data)

    @app.error()
    def error(exception: Exception, outer_middleware_data: str):
        assert outer_middleware_data == "outer_middleware_data"
        return PlainTextResponse("Error")

    request = Mock()
    request.path = "/"
    request.method = HTTPMethod.GET

    response = app.propagate(request)

    assert response.body == "Error".encode()


def test_error_with_filter(app: Application) -> None:
    @app.get("/")
    def index():
        raise IndexError

    @app.error(lambda: True)
    def error(exception: Exception):
        return PlainTextResponse("Error")

    request = Mock()
    request.path = "/"
    request.method = HTTPMethod.GET

    response = app.propagate(request)

    assert response.body == "Error".encode()


def test_error_http_exception_status_code_filter(app: Application) -> None:
    @app.get("/")
    def index():
        raise HTTPException(status_code=HTTPStatus.IM_A_TEAPOT)

    @app.error(HTTPExceptionStatusCodeFilter(HTTPStatus.IM_A_TEAPOT))
    def error(exception: HTTPException):
        return PlainTextResponse("Error", status_code=exception.status_code)

    request = Mock()
    request.path = "/"
    request.method = HTTPMethod.GET

    response = app.propagate(request)

    assert response.status_code == HTTPStatus.IM_A_TEAPOT
    assert response.body == "Error".encode()


def test_error_http_exception_status_code_filter_with_wrong_status_code(
    app: Application,
) -> None:
    @app.get("/")
    def index():
        raise HTTPException(status_code=HTTPStatus.IM_A_TEAPOT)

    @app.error(HTTPExceptionStatusCodeFilter(HTTPStatus.OK))
    def error():
        assert False  # noqa: B011

    request = Mock()
    request.path = "/"
    request.method = HTTPMethod.GET

    response = app.propagate(request)

    assert response.status_code == HTTPStatus.IM_A_TEAPOT
    assert response.body == HTTPStatus.IM_A_TEAPOT.phrase.encode()


def test_skip_route(app: Application) -> None:
    @app.get("/")
    def index():
        raise Exception("Error in index")

    @app.error()
    def error():
        raise SkipRoute

    request = Mock()
    request.path = "/"
    request.method = HTTPMethod.GET

    with pytest.raises(Exception, match="Error in index"):
        app.propagate(request)


def test_propagate_error(app: Application) -> None:
    @app.error()
    def error(exception: Exception):
        assert str(exception) == "Error"

    app.propagate_error(Exception("Error"))


def test_http_exception(app: Application) -> None:
    @app.get("/")
    def index():
        raise HTTPException(status_code=HTTPStatus.IM_A_TEAPOT)

    request = Mock()
    request.path = "/"
    request.method = HTTPMethod.GET

    response = app.propagate(request)

    assert response.status_code == HTTPStatus.IM_A_TEAPOT
    assert response.body == HTTPStatus.IM_A_TEAPOT.phrase.encode()


def test_http_exception_with_detail(app: Application) -> None:
    @app.get("/")
    def index():
        raise HTTPException(
            status_code=HTTPStatus.IM_A_TEAPOT,
            detail="I'm a teapot with detail",
        )

    request = Mock()
    request.path = "/"
    request.method = HTTPMethod.GET

    response = app.propagate(request)

    assert response.status_code == HTTPStatus.IM_A_TEAPOT
    assert response.body == "I'm a teapot with detail".encode()


def test_http_exception_with_headers(app: Application) -> None:
    @app.get("/")
    def index():
        raise HTTPException(
            status_code=HTTPStatus.IM_A_TEAPOT, headers={"X-Header": "Value"}
        )

    request = Mock()
    request.path = "/"
    request.method = HTTPMethod.GET

    response = app.propagate(request)

    assert response.status_code == HTTPStatus.IM_A_TEAPOT
    assert response.body == HTTPStatus.IM_A_TEAPOT.phrase.encode()
    assert response.headers["X-Header"] == "Value"
