from contextlib import AbstractContextManager, nullcontext
from http import HTTPStatus
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


def test_register_error(app: Application) -> None:
    mocked_error_handler = Mock()
    app.error.register(mocked_error_handler)

    assert any(error.callback is mocked_error_handler for error in app.error)


def test_register_error_via_decorator(app: Application) -> None:
    @app.error()
    def error_handler():
        pass

    assert any(error.callback is error_handler for error in app.error)


def test_propagate_error(app: Application, mocked_request: Mock) -> None:
    @app.error()
    def error(exception: Exception):
        assert isinstance(exception, Exception)
        assert str(exception) == "Error"

    app.propagate_error(Exception("Error"), request=mocked_request)


def test_errors_is_alias_for_error(app: Application) -> None:
    assert app.errors is app.error


def test_error(app: Application, mocked_request: Mock) -> None:
    @app.get("/")
    def index():
        raise Exception

    @app.error()
    def error():
        return PlainTextResponse("Error")

    response = app.propagate(mocked_request)

    assert response.content == "Error"


def test_multiple_errors(app: Application, mocked_request: Mock) -> None:
    @app.get("/")
    def index():
        raise Exception

    @app.error()
    def error():
        return PlainTextResponse("Error")

    @app.error()
    def error2():
        assert False  # noqa: B011

    response = app.propagate(mocked_request)

    assert response.content == "Error"


def test_do_not_handle_error(app: Application, mocked_request: Mock) -> None:
    @app.get("/")
    def index():
        raise Exception("Error in index")

    @app.error(ExceptionTypeFilter(IndexError))
    def error():
        assert False  # noqa: B011

    with pytest.raises(Exception, match="Error in index"):
        app.propagate(mocked_request)


def test_handle_error_by_type(app: Application, mocked_request: Mock) -> None:
    @app.get("/")
    def index():
        raise IndexError

    @app.error(ExceptionTypeFilter(IndexError))
    def error():
        return PlainTextResponse("Error")

    response = app.propagate(mocked_request)

    assert response.content == "Error"


def test_error_with_root_filter(
    app: Application, mocked_request: Mock
) -> None:
    app.error.filter(ExceptionTypeFilter(IndexError))

    @app.get("/")
    def index():
        raise Exception("Error in index")

    @app.error()
    def error():
        assert False  # noqa: B011

    with pytest.raises(Exception, match="Error in index"):
        app.propagate(mocked_request)


def test_error_middleware(app: Application, mocked_request: Mock) -> None:
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
    def error(middleware_data: str):
        assert middleware_data == "middleware_data"
        return PlainTextResponse("Error")

    response = app.propagate(mocked_request)

    assert response.content == "Error"


def test_error_outer_middleware(
    app: Application, mocked_request: Mock
) -> None:
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
    def error(outer_middleware_data: str):
        assert outer_middleware_data == "outer_middleware_data"
        return PlainTextResponse("Error")

    response = app.propagate(mocked_request)

    assert response.content == "Error"


def test_error_with_filter(app: Application, mocked_request: Mock) -> None:
    @app.get("/")
    def index():
        raise IndexError

    @app.error(lambda: True)
    def error():
        return PlainTextResponse("Error")

    response = app.propagate(mocked_request)

    assert response.content == "Error"


@pytest.mark.parametrize(
    "exceptions, contextmanager",
    [
        (
            [ValueError],
            nullcontext(),
        ),
        (
            [KeyError, ValueError],
            nullcontext(),
        ),
        (
            [list],
            pytest.raises(
                TypeError,
                match="exception should be subclass of Exception not 'list'",
            ),
        ),
        (
            [],
            pytest.raises(
                ValueError, match="At least one exception type is required"
            ),
        ),
    ],
)
def test_create_exception_type_filter(
    app: Application,
    exceptions: list[type[Exception]],
    contextmanager: AbstractContextManager,
) -> None:
    with contextmanager:
        ExceptionTypeFilter(*exceptions)


@pytest.mark.parametrize(
    "status_codes, contextmanager",
    [
        (
            [HTTPStatus.INTERNAL_SERVER_ERROR],
            nullcontext(),
        ),
        (
            [HTTPStatus.INTERNAL_SERVER_ERROR, HTTPStatus.BAD_REQUEST],
            nullcontext(),
        ),
        (
            [999],
            pytest.raises(ValueError, match="Invalid status code: 999"),
        ),
        (
            [],
            pytest.raises(
                ValueError, match="At least one status code is required"
            ),
        ),
    ],
)
def test_create_http_exception_status_code_filter(
    app: Application,
    status_codes: list[int],
    contextmanager: AbstractContextManager,
) -> None:
    with contextmanager:
        HTTPExceptionStatusCodeFilter(*status_codes)


def test_error_http_exception_status_code_filter(
    app: Application, mocked_request: Mock
) -> None:
    @app.get("/")
    def index():
        raise HTTPException(status_code=HTTPStatus.IM_A_TEAPOT)

    @app.error(HTTPExceptionStatusCodeFilter(HTTPStatus.IM_A_TEAPOT))
    def error(exception: HTTPException):
        return PlainTextResponse("Error", status_code=exception.status_code)

    response = app.propagate(mocked_request)

    assert response.status_code == HTTPStatus.IM_A_TEAPOT
    assert response.content == "Error"


def test_error_http_exception_status_code_filter_with_wrong_status_code(
    app: Application, mocked_request: Mock
) -> None:
    @app.get("/")
    def index():
        raise HTTPException(status_code=HTTPStatus.IM_A_TEAPOT)

    @app.error(HTTPExceptionStatusCodeFilter(HTTPStatus.OK))
    def error():
        assert False  # noqa: B011

    response = app.propagate(mocked_request)

    assert response.status_code == HTTPStatus.IM_A_TEAPOT
    assert response.content == {"detail": HTTPStatus.IM_A_TEAPOT.phrase}


def test_error_http_exception_status_code_filter_with_wrong_exception_type(
    app: Application, mocked_request: Mock
) -> None:
    @app.get("/")
    def index():
        raise Exception("Error in index")

    @app.error(HTTPExceptionStatusCodeFilter(HTTPStatus.IM_A_TEAPOT))
    def error():
        assert False  # noqa: B011

    with pytest.raises(Exception, match="Error in index"):
        app.propagate(mocked_request)


def test_skip_route(app: Application, mocked_request: Mock) -> None:
    @app.get("/")
    def index():
        raise Exception("Error in index")

    @app.error()
    def error():
        raise SkipRoute

    with pytest.raises(Exception, match="Error in index"):
        app.propagate(mocked_request)
