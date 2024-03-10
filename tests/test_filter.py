from unittest.mock import Mock

import pytest

from mini_framework import Application, Router
from mini_framework.filters import BaseFilter
from mini_framework.responses import PlainTextResponse
from mini_framework.routes.manager import UNHANDLED


def test_register_filter(app: Application) -> None:
    app.filter(lambda: True)


def test_register_filter_via_base_filter(app: Application) -> None:
    class Filter(BaseFilter):
        def __call__(self) -> bool:
            return True

    app.filter(Filter())


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
    mocked_request: Mock,
) -> None:
    router1 = Router()
    router2 = Router()

    mocked_filter1 = Mock(return_value=filter1_return_value)
    mocked_filter2 = Mock(return_value=filter2_return_value)

    router1.get("/", mocked_filter1)(lambda: PlainTextResponse("first"))
    router2.get("/", mocked_filter2)(lambda: PlainTextResponse("second"))

    app.include_router(router1)
    app.include_router(router2)

    response = app.propagate(mocked_request)

    if expected_result is UNHANDLED:
        assert response is UNHANDLED
    else:
        assert response.content == expected_result

    if filter1_return_value and filter2_return_value:
        mocked_filter1.assert_called_once()
        mocked_filter2.assert_not_called()
    elif filter1_return_value and not filter2_return_value:
        mocked_filter1.assert_called_once()
    elif filter2_return_value and not filter1_return_value:
        mocked_filter2.assert_called_once()


def test_multiple_routers_with_filters_and_router_without_filters_propagation(
    app: Application, mocked_request: Mock
) -> None:
    router1 = Router()
    router2 = Router()

    router1.get("/", lambda: False)(lambda: PlainTextResponse("first"))
    router2.get("/")(lambda: PlainTextResponse("second"))

    app.include_router(router1)
    app.include_router(router2)

    response = app.propagate(mocked_request)

    assert response.content == "second"


def test_multiple_routers_and_filters_not_handled_propagation(
    app: Application, mocked_request: Mock
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

    response = app.propagate(mocked_request)

    assert response is UNHANDLED
    mocked_filter_for_router1.assert_called_once()
    mocked_filter_for_router2.assert_called_once()


def test_router_filters_do_not_affect_to_another_router(
    app: Application, mocked_request: Mock
) -> None:
    mocked_callback = Mock(return_value=None)
    mocked_callback.__name__ = "name"

    router1 = Router()
    router1.filter(lambda: False)

    router2 = Router()

    app.include_router(router1)
    app.include_router(router2)

    router2.get("/")(mocked_callback)

    app.propagate(mocked_request)

    mocked_callback.assert_called_once()


def test_router_filters_affect_to_sub_router(
    app: Application, mocked_request: Mock
) -> None:
    mocked_callback = Mock()
    mocked_callback.__name__ = "name"

    router1 = Router()
    router1.filter(lambda: False)

    router2 = Router()

    router1.include_router(router2)

    app.include_router(router1)

    router2.get("/")(mocked_callback)

    app.propagate(mocked_request)

    mocked_callback.assert_not_called()


def test_filter_dependency_injection(
    app: Application, mocked_request: Mock
) -> None:
    mocked_callback = Mock(return_value=None)
    mocked_callback.__name__ = "name"

    app.get("/", lambda route: route.path == "/")(mocked_callback)

    app.propagate(mocked_request)

    mocked_callback.assert_called_once()


def test_filter_and_route_not_triggered(
    app: Application, mocked_request: Mock
) -> None:
    mocked_callback = Mock()
    mocked_callback.__name__ = "name"
    mocked_filter = Mock()

    app.get("/", lambda: False, mocked_filter)(mocked_callback)

    app.propagate(mocked_request)

    mocked_callback.assert_not_called()
    mocked_filter.assert_not_called()


def test_filter_not_triggered_for_app_with_filter(
    app: Application, mocked_request: Mock
) -> None:
    mocked_callback = Mock()
    mocked_callback.__name__ = "name"
    mocked_filter = Mock()

    app.filter(lambda: False)
    app.get("/", lambda: mocked_filter)(mocked_callback)

    app.propagate(mocked_request)

    mocked_callback.assert_not_called()
    mocked_filter.assert_not_called()
