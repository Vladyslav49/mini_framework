from http import HTTPMethod
from unittest.mock import Mock

from mini_framework import Application, Router
from mini_framework.routes.route import Route


def test_successful_route_resolution(app: Application) -> None:
    mocked_callback = Mock()

    app.get("/", lambda: True)(mocked_callback)

    app.propagate("/", method=HTTPMethod.GET)

    mocked_callback.assert_called_once()


def test_unsuccessful_route_resolution(app: Application) -> None:
    mocked_callback = Mock()

    app.get("/", lambda: False)(mocked_callback)

    app.propagate("/", method=HTTPMethod.GET)

    mocked_callback.assert_not_called()


def test_successful_route_with_multiple_routes(app: Application) -> None:
    mocked_callback = Mock()

    app.get("/", lambda: True, lambda: True)(mocked_callback)

    app.propagate("/", method=HTTPMethod.GET)

    mocked_callback.assert_called_once()


def test_route_not_triggered(app: Application) -> None:
    mocked_callback = Mock()
    mocked_filter = Mock(return_value=True)

    app.get("/", mocked_filter, lambda: False)(mocked_callback)

    app.propagate("/", method=HTTPMethod.GET)

    mocked_callback.assert_not_called()
    mocked_filter.assert_called_once()


def test_filter_and_route_not_triggered(app: Application) -> None:
    mocked_callback = Mock()
    mocked_filter = Mock()

    app.get("/", lambda: False, mocked_filter)(mocked_callback)

    app.propagate("/", method=HTTPMethod.GET)

    mocked_callback.assert_not_called()
    mocked_filter.assert_not_called()


def test_filter_not_triggered_for_app_with_filter(app: Application) -> None:
    mocked_callback = Mock()
    mocked_filter = Mock()

    app.filter(lambda: False)
    app.get("/", lambda: mocked_filter)(mocked_callback)

    app.propagate("/", method=HTTPMethod.GET)

    mocked_callback.assert_not_called()
    mocked_filter.assert_not_called()


def test_router_filters_do_not_affect_to_another_router(
    app: Application,
) -> None:
    mocked_callback = Mock()

    router1 = Router()
    router1.filter(lambda: False)

    router2 = Router()

    app.include_router(router1)
    app.include_router(router2)

    router2.get("/")(mocked_callback)

    app.propagate("/", method=HTTPMethod.GET)

    mocked_callback.assert_called_once()


def test_router_filters_affect_to_sub_router(app: Application) -> None:
    mocked_callback = Mock()

    router1 = Router()
    router1.filter(lambda: False)

    router2 = Router()

    router1.include_router(router2)

    app.include_router(router1)

    router2.get("/")(mocked_callback)

    app.propagate("/", method=HTTPMethod.GET)

    mocked_callback.assert_not_called()


def test_filter_dependency_injection(app: Application) -> None:
    mocked_callback = Mock()

    def filter_path(route: Route) -> bool:
        return route.path == "/"

    app.get("/", filter_path)(mocked_callback)

    app.propagate("/", method=HTTPMethod.GET)

    mocked_callback.assert_called_once()
