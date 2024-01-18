from http import HTTPMethod, HTTPStatus
from typing import Any

import pytest

from mini_framework import Application
from mini_framework.exceptions import HTTPException
from mini_framework.filters.exception import (
    ExceptionTypeFilter,
    HTTPExceptionStatusCodeFilter,
)
from mini_framework.middlewares.base import CallNext
from mini_framework.responses import PlainTextResponse, Response
from mini_framework.routes.manager import SkipRoute


def test_error_is_alias_for_errors(app: Application) -> None:
    assert app.error is app.errors


def test_error(app: Application) -> None:
    @app.get("/")
    def index():
        raise Exception

    @app.error()
    def error(exception: Exception):
        return PlainTextResponse(content="Error")

    response: Response = app.propagate("/", method=HTTPMethod.GET)

    assert response.render() == "Error".encode()


def test_multiple_errors(app: Application) -> None:
    @app.get("/")
    def index():
        raise Exception

    @app.error()
    def error(exception: Exception):
        return PlainTextResponse(content="Error")

    @app.error()
    def error2(exception: Exception):
        assert False  # noqa: B011

    response: Response = app.propagate("/", method=HTTPMethod.GET)

    assert response.render() == "Error".encode()


def test_error_type(app: Application) -> None:
    @app.get("/")
    def index():
        raise IndexError

    @app.error()
    def error(exception: Exception):
        assert isinstance(exception, IndexError)
        return PlainTextResponse(content="Error")

    app.propagate("/", method=HTTPMethod.GET)


def test_do_not_handle_error(app: Application) -> None:
    @app.get("/")
    def index():
        raise Exception("Error in index")

    @app.error(ExceptionTypeFilter(IndexError))
    def error(exception: Exception):
        assert False  # noqa: B011

    with pytest.raises(Exception, match="Error in index"):
        app.propagate("/", method=HTTPMethod.GET)


def test_handle_error_by_type(app: Application) -> None:
    @app.get("/")
    def index():
        raise IndexError

    @app.error(ExceptionTypeFilter(IndexError))
    def error(exception: Exception):
        return PlainTextResponse(content="Error")

    response: Response = app.propagate("/", method=HTTPMethod.GET)

    assert response.render() == "Error".encode()


def test_error_with_root_filter(app: Application) -> None:
    app.error.filter(ExceptionTypeFilter(IndexError))

    @app.get("/")
    def index():
        raise Exception("Error in index")

    @app.error()
    def error(exception: Exception):
        assert False  # noqa: B011

    with pytest.raises(Exception, match="Error in index"):
        app.propagate("/", method=HTTPMethod.GET)


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
        return PlainTextResponse(content="Error")

    response: Response = app.propagate("/", method=HTTPMethod.GET)

    assert response.render() == "Error".encode()


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
        return PlainTextResponse(content="Error")

    response: Response = app.propagate("/", method=HTTPMethod.GET)

    assert response.render() == "Error".encode()


def test_error_with_filter(app: Application) -> None:
    @app.get("/")
    def index():
        raise IndexError

    @app.error(lambda: True)
    def error(exception: Exception):
        return PlainTextResponse(content="Error")

    response: Response = app.propagate("/", method=HTTPMethod.GET)

    assert response.render() == "Error".encode()


def test_error_http_exception_status_code_filter(app: Application) -> None:
    @app.get("/")
    def index():
        raise HTTPException(status_code=HTTPStatus.IM_A_TEAPOT)

    @app.error(HTTPExceptionStatusCodeFilter(HTTPStatus.IM_A_TEAPOT))
    def error(exception: Exception):
        return True

    response: Response = app.propagate("/", method=HTTPMethod.GET)

    assert response.status_code == HTTPStatus.IM_A_TEAPOT
    assert response.render() == HTTPStatus.IM_A_TEAPOT.phrase.encode()


def test_error_http_exception_status_code_filter_with_wrong_status_code(
    app: Application,
) -> None:
    @app.get("/")
    def index():
        raise HTTPException(status_code=HTTPStatus.IM_A_TEAPOT)

    @app.error(HTTPExceptionStatusCodeFilter(HTTPStatus.OK))
    def error(exception: Exception):
        assert False  # noqa: B011

    response: Response = app.propagate("/", method=HTTPMethod.GET)

    assert response.status_code == HTTPStatus.IM_A_TEAPOT
    assert response.render() == HTTPStatus.IM_A_TEAPOT.phrase.encode()


def test_skip_route(app: Application) -> None:
    @app.get("/")
    def index():
        raise Exception("Error in index")

    @app.error()
    def error(exception: Exception):
        raise SkipRoute

    with pytest.raises(Exception, match="Error in index"):
        app.propagate("/", method=HTTPMethod.GET)


def test_propagate_error(app: Application) -> None:
    @app.error()
    def error(exception: Exception):
        assert str(exception) == "Error"

    app.propagate_error(Exception("Error"), {})


def test_http_exception(app: Application) -> None:
    @app.get("/")
    def index():
        raise HTTPException(status_code=HTTPStatus.IM_A_TEAPOT)

    response: Response = app.propagate("/", method=HTTPMethod.GET)

    assert response.status_code == HTTPStatus.IM_A_TEAPOT
    assert response.render() == HTTPStatus.IM_A_TEAPOT.phrase.encode()


def test_http_exception_with_detail(app: Application) -> None:
    @app.get("/")
    def index():
        raise HTTPException(
            status_code=HTTPStatus.IM_A_TEAPOT,
            detail="I'm a teapot with detail",
        )

    response: Response = app.propagate("/", method=HTTPMethod.GET)

    assert response.status_code == HTTPStatus.IM_A_TEAPOT
    assert response.render() == "I'm a teapot with detail".encode()


def test_http_exception_with_headers(app: Application) -> None:
    @app.get("/")
    def index():
        raise HTTPException(
            status_code=HTTPStatus.IM_A_TEAPOT,
            headers={"X-Header": "Value"},
        )

    response: Response = app.propagate("/", method=HTTPMethod.GET)

    assert response.status_code == HTTPStatus.IM_A_TEAPOT
    assert response.render() == HTTPStatus.IM_A_TEAPOT.phrase.encode()
    assert response.headers["X-Header"] == "Value"