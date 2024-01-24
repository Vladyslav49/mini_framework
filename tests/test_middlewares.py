from http import HTTPMethod
from typing import Any
from unittest.mock import Mock

from mini_framework import Application, Response
from mini_framework.middlewares.base import CallNext
from mini_framework.responses import PlainTextResponse
from mini_framework.routes.manager import SkipRoute
from mini_framework.routes.route import Route


def test_outer_middleware(app: Application) -> None:
    is_callback_called = False

    app.filter(lambda: False)

    @app.outer_middleware
    def outer_middleware(call_next: CallNext, data: dict[str, Any]) -> None:
        nonlocal is_callback_called
        call_next(data)
        is_callback_called = True

    @app.get("/")
    def index() -> None:
        assert False  # noqa: B011

    request = Mock()
    request.path = "/"
    request.method = HTTPMethod.GET

    app.propagate(request)

    assert is_callback_called


def test_get_route_in_middleware_and_callback(app: Application) -> None:
    is_callback_called = False

    @app.route.middleware
    def middleware(call_next: CallNext, data: dict[str, Any]) -> None:
        route: Route = data["route"]
        assert route.path == "/"
        assert not is_callback_called
        call_next(data)
        assert is_callback_called

    @app.get("/")
    def index(route: Route) -> None:
        assert route.path == "/"
        nonlocal is_callback_called
        is_callback_called = True

    request = Mock()
    request.path = "/"
    request.method = HTTPMethod.GET

    app.propagate(request)

    assert is_callback_called


def test_multiple_middlewares(app: Application) -> None:
    @app.route.middleware
    def middleware1(call_next: CallNext, data: dict[str, Any]) -> None:
        data["value"] = 1
        call_next(data)
        assert data["value"] == 3

    @app.route.middleware
    def middleware2(call_next: CallNext, data: dict[str, Any]) -> None:
        assert data["value"] == 1
        data["value"] += 1
        call_next(data)
        assert data["value"] == 2
        data["value"] += 1

    @app.get("/")
    def index(value: int) -> None:
        assert value == 2

    request = Mock()
    request.path = "/"
    request.method = HTTPMethod.GET

    app.propagate(request)


def test_get_response_in_middleware(app: Application) -> None:
    @app.route.middleware
    def middleware(call_next: CallNext, data: dict[str, Any]) -> None:
        response: Response = call_next(data)
        assert isinstance(response, Response)
        assert response.status_code == 200
        assert response.body == "Hello, World!".encode()

    @app.get("/")
    def index():
        return PlainTextResponse("Hello, World!")

    request = Mock()
    request.path = "/"
    request.method = HTTPMethod.GET

    app.propagate(request)


def test_skip_route_in_middleware(app: Application) -> None:
    @app.route.middleware
    def middleware(call_next: CallNext, data: dict[str, Any]) -> None:
        raise SkipRoute

    @app.get("/")
    def index() -> None:
        assert False  # noqa: B011

    request = Mock()
    request.path = "/"
    request.method = HTTPMethod.GET

    app.propagate(request)
