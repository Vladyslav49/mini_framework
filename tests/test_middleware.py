from http import HTTPStatus
from typing import Any
from unittest.mock import Mock


from mini_framework import Application, Response
from mini_framework.middlewares import BaseMiddleware
from mini_framework.middlewares.base import CallNext
from mini_framework.responses import PlainTextResponse
from mini_framework.routes.manager import SkipRoute, UNHANDLED
from mini_framework.routes.route import Route


def test_register_middleware(app: Application) -> None:
    mocked_middleware = Mock()
    app.route.middleware.register(mocked_middleware)

    assert any(m is mocked_middleware for m in app.route.middleware)


def test_register_middleware_via_decorator(app: Application) -> None:
    @app.route.middleware
    def middleware(call_next: CallNext, data: dict[str, Any]) -> None:
        pass

    assert any(m is middleware for m in app.route.middleware)


def test_register_middleware_via_base_middleware(app: Application) -> None:
    class Middleware(BaseMiddleware):
        def __call__(self, call_next: CallNext, data: dict[str, Any]) -> Any:
            return call_next(data)

    middleware = Middleware()

    app.route.middleware.register(middleware)

    assert any(m is middleware for m in app.route.middleware)


def test_outer_middleware(app: Application, mock_request: Mock) -> None:
    is_callback_called = False

    app.filter(lambda: False)

    @app.outer_middleware
    def outer_middleware(call_next: CallNext, data: dict[str, Any]) -> None:
        nonlocal is_callback_called
        call_next(data)
        is_callback_called = True

    @app.get("/")
    def index():
        assert False  # noqa: B011

    app.propagate(mock_request)

    assert is_callback_called


def test_get_route_in_middleware_and_callback(
    app: Application, mock_request: Mock
) -> None:
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

    app.propagate(mock_request)

    assert is_callback_called


def test_multiple_middlewares(app: Application, mock_request: Mock) -> None:
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

    app.propagate(mock_request)


def test_get_response_in_middleware(
    app: Application, mock_request: Mock
) -> None:
    @app.route.middleware
    def middleware(call_next: CallNext, data: dict[str, Any]) -> None:
        response: Response = call_next(data)
        assert isinstance(response, Response)
        assert response.status_code == HTTPStatus.OK
        assert response.content == "Hello, World!"

    @app.get("/")
    def index():
        return PlainTextResponse("Hello, World!")

    app.propagate(mock_request)


def test_skip_route_in_middleware(
    app: Application, mock_request: Mock
) -> None:
    @app.middleware
    def middleware(call_next: CallNext, data: dict[str, Any]):
        raise SkipRoute

    @app.get("/")
    def index():
        assert False  # noqa: B011

    response = app.propagate(mock_request)

    assert response is UNHANDLED
