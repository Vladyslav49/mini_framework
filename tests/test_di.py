from http import HTTPMethod
from typing import Any
from unittest.mock import Mock

from mini_framework import Application
from mini_framework.middlewares.base import CallNext


def test_di_via_middleware(app: Application) -> None:
    @app.route.middleware
    def middleware(call_next: CallNext, data: dict[str, Any]) -> None:
        data["some_data"] = "some_data"
        call_next(data)

    @app.get("/")
    def index(some_data: str) -> None:
        assert some_data == "some_data"

    request = Mock()
    request.path = "/"
    request.method = HTTPMethod.GET

    app.propagate(request)


def test_di_via_outer_middleware(app: Application) -> None:
    @app.outer_middleware
    def outer_middleware(call_next: CallNext, data: dict[str, Any]) -> None:
        data["some_data"] = "some_data"
        call_next(data)

    @app.get("/")
    def index(some_data: str) -> None:
        assert some_data == "some_data"

    request = Mock()
    request.path = "/"
    request.method = HTTPMethod.GET

    app.propagate(request)


def test_di_via_application_kwargs() -> None:
    app = Application(some_data="some_data")

    @app.get("/")
    def index(some_data: str) -> None:
        assert some_data == "some_data"

    request = Mock()
    request.path = "/"
    request.method = HTTPMethod.GET

    app.propagate(request)


def test_di_via_application_setitem(app: Application) -> None:
    app["some_data"] = "some_data"

    @app.get("/")
    def index(some_data: str) -> None:
        assert some_data == "some_data"

    request = Mock()
    request.path = "/"
    request.method = HTTPMethod.GET

    app.propagate(request)


def test_di_via_filter(app: Application) -> None:
    def filter() -> dict[str, int]:
        return {"value": 0}

    @app.get("/", filter)
    def index(value: int) -> None:
        assert value == 0

    request = Mock()
    request.path = "/"
    request.method = HTTPMethod.GET

    app.propagate(request)
