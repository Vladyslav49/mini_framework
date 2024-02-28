from typing import Any
from unittest.mock import Mock

from mini_framework import Application
from mini_framework.middlewares.base import CallNext


def test_di_via_middleware(app: Application, mock_request: Mock) -> None:
    @app.route.middleware
    def middleware(call_next: CallNext, data: dict[str, Any]) -> None:
        data["some_data"] = "some_data"
        call_next(data)

    @app.get("/")
    def index(some_data: str) -> None:
        assert some_data == "some_data"

    app.propagate(mock_request)


def test_di_via_outer_middleware(app: Application, mock_request: Mock) -> None:
    @app.outer_middleware
    def outer_middleware(call_next: CallNext, data: dict[str, Any]) -> None:
        data["some_data"] = "some_data"
        call_next(data)

    @app.get("/")
    def index(some_data: str) -> None:
        assert some_data == "some_data"

    app.propagate(mock_request)


def test_di_via_application_kwargs(mock_request: Mock) -> None:
    app = Application(some_data="some_data")

    @app.get("/")
    def index(some_data: str) -> None:
        assert some_data == "some_data"

    app.propagate(mock_request)


def test_di_via_application_setitem(
    app: Application, mock_request: Mock
) -> None:
    app["some_data"] = "some_data"

    @app.get("/")
    def index(some_data: str) -> None:
        assert some_data == "some_data"

    app.propagate(mock_request)


def test_route_di_via_filter(app: Application, mock_request: Mock) -> None:
    def filter() -> dict[str, int]:
        return {"value": 0}

    @app.get("/", filter)
    def index(value: int) -> None:
        assert value == 0

    app.propagate(mock_request)


def test_error_di_via_filter(app: Application, mock_request: Mock) -> None:
    @app.get("/")
    def index():
        raise Exception

    def filter() -> dict[str, int]:
        return {"value": 0}

    @app.error(filter)
    def error_handler(value: int) -> None:
        assert value == 0

    app.propagate(mock_request)
