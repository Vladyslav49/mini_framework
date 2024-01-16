from http import HTTPMethod

import pytest

from mini_framework import Application


@pytest.fixture
def app() -> Application:
    return Application()


def index() -> str:
    return "Hello, World!"


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
