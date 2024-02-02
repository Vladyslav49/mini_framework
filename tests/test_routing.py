from collections.abc import Callable
from http import HTTPMethod
from typing import NoReturn
from unittest.mock import Mock

import pytest

from mini_framework import Application, Router
from mini_framework.responses import PlainTextResponse
from mini_framework.routes.manager import SkipRoute, UNHANDLED


@pytest.mark.parametrize("method", list(HTTPMethod))
def test_register_route_with_specified_method(
    app: Application, method: str, mock_request: Mock
) -> None:
    mocked_callback = Mock()
    app.route.register(mocked_callback, "/", method=method)
    mock_request.method = method

    app.propagate(mock_request)

    mocked_callback.assert_called_once()


@pytest.mark.parametrize(
    "method, route",
    [(method, getattr(Router, method.lower())) for method in HTTPMethod],
)
def test_register_route_with_dynamic_route(
    app: Application, mock_request: Mock, method: str, route: Callable
) -> None:
    mocked_callback = Mock()
    route(app, "/")(mocked_callback)
    mock_request.method = method

    app.propagate(mock_request)

    mocked_callback.assert_called_once()


def test_register_via_decorator_and_get_result(
    app: Application, mock_request: Mock
) -> None:
    @app.get("/")
    def index():
        return PlainTextResponse("Hello, World!")

    response = app.propagate(mock_request)

    assert response.body == "Hello, World!".encode()


def test_not_registered_route(app: Application, mock_request: Mock) -> None:
    response = app.propagate(mock_request)

    assert response is UNHANDLED


def test_successful_route_resolution(
    app: Application, mock_request: Mock
) -> None:
    mocked_callback = Mock()

    app.get("/", lambda: True)(mocked_callback)

    app.propagate(mock_request)

    mocked_callback.assert_called_once()


def test_unsuccessful_route_resolution(
    app: Application, mock_request: Mock
) -> None:
    mocked_callback = Mock()

    app.get("/", lambda: False)(mocked_callback)

    app.propagate(mock_request)

    mocked_callback.assert_not_called()


def test_successful_route_with_multiple_routes(
    app: Application, mock_request: Mock
) -> None:
    mocked_callback = Mock()

    app.get("/", lambda: True, lambda: True)(mocked_callback)

    app.propagate(mock_request)

    mocked_callback.assert_called_once()


def test_route_not_triggered(app: Application, mock_request: Mock) -> None:
    mocked_callback = Mock()
    mocked_filter = Mock(return_value=True)

    app.get("/", mocked_filter, lambda: False)(mocked_callback)

    app.propagate(mock_request)

    mocked_callback.assert_not_called()
    mocked_filter.assert_called_once()


def test_skip_route(app: Application, mock_request: Mock) -> None:
    @app.get("/")
    def index() -> NoReturn:
        raise SkipRoute

    response = app.propagate(mock_request)

    assert response is UNHANDLED


def test_get_routers_and_routes(app: Application, mock_request: Mock) -> None:
    mock_request.path_params = {}

    router1 = Router()
    router2 = Router()
    router3 = Router()

    route1 = lambda: True  # noqa: E731
    route2 = lambda: True  # noqa: E731

    router1.get("/")(route1)
    router2.get("/")(route2)

    app.include_router(router1)
    app.include_router(router2)
    app.include_router(router3)

    routers_and_routes = list(app._get_routers_and_routes(mock_request))

    routers_and_callbacks = [
        (router, route.callback) for router, route in routers_and_routes
    ]

    assert routers_and_callbacks == [
        (router1, route1),
        (router2, route2),
    ]


@pytest.mark.parametrize(
    "path, method",
    [
        ("/path/", HTTPMethod.GET),
        ("/", HTTPMethod.POST),
        ("/path/", HTTPMethod.POST),
    ],
)
def test_get_routers_not_found(
    app: Application, mock_request: Mock, path: str, method: str
) -> None:
    mock_request.path = path
    mock_request.method = method

    router1 = Router()
    router2 = Router()

    route1 = lambda: True  # noqa: E731

    router1.get("/")(route1)

    app.include_router(router1)
    app.include_router(router2)

    routers_and_routes = list(app._get_routers_and_routes(mock_request))

    assert routers_and_routes == []


def test_multiple_routers_propagation(
    app: Application, mock_request: Mock
) -> None:
    router1 = Router()
    router2 = Router()
    router3 = Router()
    mocked_filter = Mock(return_value=False)

    router1.get("/")(lambda: PlainTextResponse("first"))
    router2.get("/")(lambda: PlainTextResponse("second"))
    router3.get("/", mocked_filter)(lambda: PlainTextResponse("third"))

    app.include_router(router1)
    app.include_router(router2)
    app.include_router(router3)

    response = app.propagate(mock_request)

    assert response.body == "first".encode()
    mocked_filter.assert_not_called()
