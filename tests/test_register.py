from http import HTTPMethod

import pytest

from mini_framework import Application, Router


def index() -> str:
    return "Hello, World!"


def test_include_router(app: Application) -> None:
    router = Router()

    app.include_router(router)

    assert router.parent_router is app


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
        app.include_router("some")  # pyright: ignore[reportGeneralTypeIssues]


def test_router_is_already_attached(app: Application) -> None:
    router1 = Router()
    router2 = Router()

    router1.include_router(router2)

    with pytest.raises(
        RuntimeError,
        match=f"Router is already attached to {router1!r}",
    ):
        app.include_router(router2)


def test_router_chain_tail() -> None:
    router1 = Router()
    router2 = Router()
    router3 = Router()
    router4 = Router()

    router1.include_router(router2)
    router2.include_router(router3)
    router2.include_router(router4)

    assert list(router1.chain_tail) == [router1, router2, router3, router4]


def test_application_parent_router() -> None:
    app = Application()

    assert app.parent_router is None


def test_change_application_parent_router(app: Application) -> None:
    router = Router()

    with pytest.raises(
        RuntimeError,
        match="Application can not be attached to another Router.",
    ):
        app.parent_router = router


def test_register(app: Application) -> None:
    app.route("/", method="GET")(index)

    route = app._get_route("/", HTTPMethod.GET)

    assert route is not None


def test_register_decorator(app: Application) -> None:
    @app.route("/", method=HTTPMethod.GET)
    def index() -> str:
        return "Hello, World!"

    route = app._get_route("/", "GET")

    assert route is not None


def test_register_get_method(app: Application) -> None:
    app.get("/")(index)

    route = app._get_route("/", HTTPMethod.GET)

    assert route is not None


def test_register_post_method(app: Application) -> None:
    app.post("/")(index)

    route = app._get_route("/", HTTPMethod.POST)

    assert route is not None


def test_register_put_method(app: Application) -> None:
    app.put("/")(index)

    route = app._get_route("/", HTTPMethod.PUT)

    assert route is not None


def test_register_patch_method(app: Application) -> None:
    app.patch("/")(index)

    route = app._get_route("/", HTTPMethod.PATCH)

    assert route is not None


def test_register_delete_method(app: Application) -> None:
    app.delete("/")(index)

    route = app._get_route("/", HTTPMethod.DELETE)

    assert route is not None


def test_not_registered_route(app: Application) -> None:
    route = app._get_route("/", HTTPMethod.GET)

    assert route is None


def test_register_same_route(app: Application) -> None:
    app.get("/")(index)

    with pytest.raises(
        ValueError,
        match="Route for path '/' and method 'GET' already exists",
    ):
        app.get("/")(index)
