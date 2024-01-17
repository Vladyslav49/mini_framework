from http import HTTPMethod
from unittest.mock import Mock

import pytest

from mini_framework import Application, Router
from mini_framework.managers.routes import UNHANDLED


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
        RuntimeError,
        match="Self-referencing routers is not allowed",
    ):
        router.include_router(router)


def test_include_router_circular_reference() -> None:
    router1 = Router()
    router2 = Router()

    router1.include_router(router2)

    with pytest.raises(
        RuntimeError,
        match="Circular referencing of Router is not allowed",
    ):
        router2.include_router(router1)


def test_include_router_not_router(app: Application) -> None:
    with pytest.raises(
        ValueError,
        match="router should be instance of Router not 'str'",
    ):
        app.include_router("some")  # type: ignore[arg-type]


def test_router_is_already_attached(app: Application) -> None:
    router1 = Router()
    router2 = Router()

    router1.include_router(router2)

    with pytest.raises(
        RuntimeError,
        match=f"Router is already attached to {router1!r}",
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


def test_get_routers(app: Application) -> None:
    router1 = Router()
    router2 = Router()
    router3 = Router()

    router1.get("/")(lambda: True)
    router2.get("/")(lambda: True)

    app.include_router(router1)
    app.include_router(router2)
    app.include_router(router3)

    routers = app._get_routers("/", method=HTTPMethod.GET)

    assert list(routers) == [router1, router2]


@pytest.mark.parametrize(
    "path, method",
    [
        ("/path/", HTTPMethod.GET),
        ("/", HTTPMethod.POST),
        ("/path/", HTTPMethod.POST),
    ],
)
def test_get_routers_not_found(
    app: Application,
    path: str,
    method: str,
) -> None:
    router1 = Router()
    router2 = Router()

    router1.get("/")(lambda: True)

    app.include_router(router1)
    app.include_router(router2)

    routers = app._get_routers(path, method=method)

    assert list(routers) == []


def test_multiple_routers_propagation(app: Application) -> None:
    router1 = Router()
    router2 = Router()
    router3 = Router()
    mocked_filter = Mock(return_value=False)

    router1.get("/")(lambda: "first")
    router2.get("/")(lambda: "second")
    router3.get("/", mocked_filter)(lambda: "third")

    app.include_router(router1)
    app.include_router(router2)
    app.include_router(router3)

    result, _ = app.propagate("/", method=HTTPMethod.GET)

    assert result == "first"
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

    router1.get("/", mocked_filter1)(lambda: "first")
    router2.get("/", mocked_filter2)(lambda: "second")

    app.include_router(router1)
    app.include_router(router2)

    result, _ = app.propagate("/", method=HTTPMethod.GET)

    assert result == expected_result

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

    router1.get("/", lambda: False)(lambda: "first")
    router2.get("/")(lambda: "second")

    app.include_router(router1)
    app.include_router(router2)

    result, _ = app.propagate("/", method=HTTPMethod.GET)

    assert result == "second"


def test_multiple_routers_and_filters_not_handled_propagation(
    app: Application,
) -> None:
    router1 = Router()
    router2 = Router()

    mocked_filter_for_router1 = Mock(return_value=False)
    mocked_filter_for_router2 = Mock(return_value=False)

    router1.get("/", mocked_filter_for_router1)(lambda: "first")
    router2.get("/", mocked_filter_for_router2)(lambda: "second")

    app.include_router(router1)
    app.include_router(router2)

    result, _ = app.propagate("/", method=HTTPMethod.GET)

    assert result is UNHANDLED
    mocked_filter_for_router1.assert_called_once()
    mocked_filter_for_router2.assert_called_once()


def test_register_route(app: Application) -> None:
    mocked_callback = Mock()
    app.routes.register(mocked_callback, "/", method="GET")

    app.propagate("/", method=HTTPMethod.GET)

    mocked_callback.assert_called_once()


def test_register_via_decorator_and_get_result(app: Application) -> None:
    @app.get("/")
    def index() -> str:
        return "Hello, World!"

    result, _ = app.propagate("/", method=HTTPMethod.GET)

    assert result == "Hello, World!"


def test_register_connect_method(app: Application) -> None:
    mocked_callback = Mock()
    app.connect("/")(mocked_callback)

    app.propagate("/", method=HTTPMethod.CONNECT)

    mocked_callback.assert_called_once()


def test_register_delete_method(app: Application) -> None:
    mocked_callback = Mock()
    app.delete("/")(mocked_callback)

    app.propagate("/", method=HTTPMethod.DELETE)

    mocked_callback.assert_called_once()


def test_register_get_method(app: Application) -> None:
    mocked_callback = Mock()
    app.get("/")(mocked_callback)

    app.propagate("/", method=HTTPMethod.GET)

    mocked_callback.assert_called_once()


def test_register_head_method(app: Application) -> None:
    mocked_callback = Mock()
    app.head("/")(mocked_callback)

    app.propagate("/", method=HTTPMethod.HEAD)

    mocked_callback.assert_called_once()


def test_register_options_method(app: Application) -> None:
    mocked_callback = Mock()
    app.options("/")(mocked_callback)

    app.propagate("/", method=HTTPMethod.OPTIONS)

    mocked_callback.assert_called_once()


def test_register_patch_method(app: Application) -> None:
    mocked_callback = Mock()
    app.patch("/")(mocked_callback)

    app.propagate("/", method=HTTPMethod.PATCH)

    mocked_callback.assert_called_once()


def test_register_post_method(app: Application) -> None:
    mocked_callback = Mock()
    app.post("/")(mocked_callback)

    app.propagate("/", method=HTTPMethod.POST)

    mocked_callback.assert_called_once()


def test_register_put_method(app: Application) -> None:
    mocked_callback = Mock()
    app.put("/")(mocked_callback)

    app.propagate("/", method=HTTPMethod.PUT)

    mocked_callback.assert_called_once()


def test_register_trace_method(app: Application) -> None:
    mocked_callback = Mock()
    app.trace("/")(mocked_callback)

    app.propagate("/", method=HTTPMethod.TRACE)

    mocked_callback.assert_called_once()


def test_not_registered_route(app: Application) -> None:
    result, _ = app.propagate("/", method=HTTPMethod.GET)

    assert result is UNHANDLED
