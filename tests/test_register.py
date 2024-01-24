from http import HTTPMethod
from typing import Any
from unittest.mock import Mock

import pytest

from mini_framework import Application, Router
from mini_framework.filters import BaseFilter
from mini_framework.middlewares.base import BaseMiddleware, CallNext
from mini_framework.responses import PlainTextResponse
from mini_framework.routes.manager import UNHANDLED


def test_application_parent_router(app: Application) -> None:
    assert app.parent_router is None


def test_include_router(app: Application) -> None:
    router = Router()

    app.include_router(router)

    assert router.parent_router is app


def test_include_application_to_router(app: Application) -> None:
    router = Router()

    with pytest.raises(
        RuntimeError,
        match="Application can not be attached to another Router.",
    ):
        router.include_router(app)


def test_include_router_self_reference() -> None:
    router = Router()

    with pytest.raises(
        RuntimeError, match="Self-referencing routers is not allowed"
    ):
        router.include_router(router)


def test_include_router_circular_reference() -> None:
    router1 = Router()
    router2 = Router()

    router1.include_router(router2)

    with pytest.raises(
        RuntimeError, match="Circular referencing of Router is not allowed"
    ):
        router2.include_router(router1)


def test_include_router_not_router(app: Application) -> None:
    with pytest.raises(
        ValueError, match="router should be instance of Router not 'str'"
    ):
        app.include_router("some")  # type: ignore[arg-type]


def test_router_is_already_attached(app: Application) -> None:
    router1 = Router()
    router2 = Router()

    router1.include_router(router2)

    with pytest.raises(
        RuntimeError, match=f"Router is already attached to {router1!r}"
    ):
        app.include_router(router2)


def test_router_chain_head() -> None:
    router1 = Router()
    router2 = Router()
    router3 = Router()

    router1.include_router(router2)
    router2.include_router(router3)

    assert list(router3.chain_head) == [router3, router2, router1]


def test_router_chain_tail() -> None:
    router1 = Router()
    router2 = Router()
    router3 = Router()
    router4 = Router()

    router1.include_router(router2)
    router2.include_router(router3)
    router2.include_router(router4)

    assert list(router1.chain_tail) == [router1, router2, router3, router4]


def test_get_routers_and_routes(app: Application) -> None:
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

    request = Mock()
    request.path = "/"
    request.method = HTTPMethod.GET
    request.path_params = {}

    routers_and_routes = list(app._get_routers_and_routes(request))

    routers_and_callbacks = [
        (router, route.callback) for (router, route) in routers_and_routes
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
    app: Application, path: str, method: str
) -> None:
    router1 = Router()
    router2 = Router()

    route1 = lambda: True  # noqa: E731

    router1.get("/")(route1)

    app.include_router(router1)
    app.include_router(router2)

    request = Mock()
    request.path = path
    request.method = method

    routers_and_routes = list(app._get_routers_and_routes(request))

    assert routers_and_routes == []


def test_multiple_routers_propagation(app: Application) -> None:
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

    request = Mock()
    request.path = "/"
    request.method = HTTPMethod.GET

    response = app.propagate(request)

    assert response.body == "first".encode()
    mocked_filter.assert_not_called()


@pytest.mark.parametrize(
    "filter1_return_value, filter2_return_value, expected_result",
    [
        (True, True, "first"),
        (True, False, "first"),
        (False, True, "second"),
        (False, False, UNHANDLED),
    ],
)
def test_multiple_routers_with_filters_propagation(
    app: Application,
    filter1_return_value: bool,
    filter2_return_value: bool,
    expected_result: str,
) -> None:
    router1 = Router()
    router2 = Router()

    mocked_filter1 = Mock(return_value=filter1_return_value)
    mocked_filter2 = Mock(return_value=filter2_return_value)

    router1.get("/", mocked_filter1)(lambda: PlainTextResponse("first"))
    router2.get("/", mocked_filter2)(lambda: PlainTextResponse("second"))

    app.include_router(router1)
    app.include_router(router2)

    request = Mock()
    request.path = "/"
    request.method = HTTPMethod.GET

    response = app.propagate(request)

    if expected_result is UNHANDLED:
        assert response is UNHANDLED
    else:
        assert response.body == expected_result.encode()

    if filter1_return_value and filter2_return_value:
        mocked_filter1.assert_called_once()
        mocked_filter2.assert_not_called()
    elif filter1_return_value and not filter2_return_value:
        mocked_filter1.assert_called_once()
    elif filter2_return_value and not filter1_return_value:
        mocked_filter2.assert_called_once()


def test_multiple_routers_with_filters_and_router_without_filters_propagation(
    app: Application,
) -> None:
    router1 = Router()
    router2 = Router()

    router1.get("/", lambda: False)(lambda: PlainTextResponse("first"))
    router2.get("/")(lambda: PlainTextResponse("second"))

    app.include_router(router1)
    app.include_router(router2)

    request = Mock()
    request.path = "/"
    request.method = HTTPMethod.GET

    response = app.propagate(request)

    assert response.body == "second".encode()


def test_multiple_routers_and_filters_not_handled_propagation(
    app: Application,
) -> None:
    router1 = Router()
    router2 = Router()

    mocked_filter_for_router1 = Mock(return_value=False)
    mocked_filter_for_router2 = Mock(return_value=False)

    router1.get("/", mocked_filter_for_router1)(
        lambda: PlainTextResponse("first")
    )
    router2.get("/", mocked_filter_for_router2)(
        lambda: PlainTextResponse("second")
    )

    app.include_router(router1)
    app.include_router(router2)

    request = Mock()
    request.path = "/"
    request.method = HTTPMethod.GET

    response = app.propagate(request)

    assert response is UNHANDLED
    mocked_filter_for_router1.assert_called_once()
    mocked_filter_for_router2.assert_called_once()


def test_register_route(app: Application) -> None:
    mocked_callback = Mock()
    app.route.register(mocked_callback, "/", method="GET")

    request = Mock()
    request.path = "/"
    request.method = HTTPMethod.GET

    app.propagate(request)

    mocked_callback.assert_called_once()


def test_register_via_decorator_and_get_result(app: Application) -> None:
    @app.get("/")
    def index():
        return PlainTextResponse("Hello, World!")

    request = Mock()
    request.path = "/"
    request.method = HTTPMethod.GET

    response = app.propagate(request)

    assert response.body == "Hello, World!".encode()


def test_register_connect_method(app: Application) -> None:
    mocked_callback = Mock()
    app.connect("/")(mocked_callback)

    request = Mock()
    request.path = "/"
    request.method = HTTPMethod.CONNECT

    app.propagate(request)

    mocked_callback.assert_called_once()


def test_register_delete_method(app: Application) -> None:
    mocked_callback = Mock()
    app.delete("/")(mocked_callback)

    request = Mock()
    request.path = "/"
    request.method = HTTPMethod.DELETE

    app.propagate(request)

    mocked_callback.assert_called_once()


def test_register_get_method(app: Application) -> None:
    mocked_callback = Mock()
    app.get("/")(mocked_callback)

    request = Mock()
    request.path = "/"
    request.method = HTTPMethod.GET

    app.propagate(request)

    mocked_callback.assert_called_once()


def test_register_head_method(app: Application) -> None:
    mocked_callback = Mock()
    app.head("/")(mocked_callback)

    request = Mock()
    request.path = "/"
    request.method = HTTPMethod.HEAD

    app.propagate(request)

    mocked_callback.assert_called_once()


def test_register_options_method(app: Application) -> None:
    mocked_callback = Mock()
    app.options("/")(mocked_callback)

    request = Mock()
    request.path = "/"
    request.method = HTTPMethod.OPTIONS

    app.propagate(request)

    mocked_callback.assert_called_once()


def test_register_patch_method(app: Application) -> None:
    mocked_callback = Mock()
    app.patch("/")(mocked_callback)

    request = Mock()
    request.path = "/"
    request.method = HTTPMethod.PATCH

    app.propagate(request)

    mocked_callback.assert_called_once()


def test_register_post_method(app: Application) -> None:
    mocked_callback = Mock()
    app.post("/")(mocked_callback)

    request = Mock()
    request.path = "/"
    request.method = HTTPMethod.POST

    app.propagate(request)

    mocked_callback.assert_called_once()


def test_register_put_method(app: Application) -> None:
    mocked_callback = Mock()
    app.put("/")(mocked_callback)

    request = Mock()
    request.path = "/"
    request.method = HTTPMethod.PUT

    app.propagate(request)

    mocked_callback.assert_called_once()


def test_register_trace_method(app: Application) -> None:
    mocked_callback = Mock()
    app.trace("/")(mocked_callback)

    request = Mock()
    request.path = "/"
    request.method = HTTPMethod.TRACE

    app.propagate(request)

    mocked_callback.assert_called_once()


def test_not_registered_route(app: Application) -> None:
    request = Mock()
    request.path = "/"
    request.method = HTTPMethod.GET

    response = app.propagate(request)

    assert response is UNHANDLED


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


def test_register_filter_via_base_filter(app: Application) -> None:
    class Filter(BaseFilter):
        def __call__(self) -> bool:
            return True

    app.filter(Filter())


def test_register_error(app: Application) -> None:
    mocked_error_handler = Mock()
    app.error.register(mocked_error_handler)

    assert any(error.callback is mocked_error_handler for error in app.error)


def test_register_error_via_decorator(app: Application) -> None:
    @app.error()
    def error_handler():
        pass

    assert any(error.callback is error_handler for error in app.error)
