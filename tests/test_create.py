from http import HTTPMethod

import pytest

from mini_framework import Application, Router
from mini_framework.routes.route import Route


def test_create_application() -> None:
    Application()


def test_create_application_with_name() -> None:
    app = Application(name="my_app")

    assert app.name == "my_app"


def test_create_router() -> None:
    Router()


def test_create_router_with_name() -> None:
    router = Router(name="my_router")

    assert router.name == "my_router"


def test_create_route() -> None:
    Route(callback=lambda: None, path="/", method=HTTPMethod.GET)


def test_create_route_with_path_without_starting_slash() -> None:
    with pytest.raises(
        ValueError, match="Path 'wrong_path' must start with '/'"
    ):
        Route(callback=lambda: None, path="wrong_path", method=HTTPMethod.GET)


def test_create_route_with_path_without_ending_slash() -> None:
    with pytest.raises(
        ValueError, match="Path '/wrong_path' must end with '/'"
    ):
        Route(callback=lambda: None, path="/wrong_path", method=HTTPMethod.GET)


def test_create_route_with_wrong_method() -> None:
    with pytest.raises(
        ValueError, match="Method 'WRONG' is not valid HTTP method"
    ):
        Route(callback=lambda: None, path="/", method="WRONG")
