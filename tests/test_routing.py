from collections.abc import Callable
from contextlib import AbstractContextManager, nullcontext
from http import HTTPMethod
from unittest.mock import Mock, create_autospec

from multipart.multipart import File

from mini_framework.datastructures import FormData, UploadFile
from mini_framework.routes.params_resolvers import resolve_upload_file_params
from mini_framework.routes.route import Route

try:
    import multipart
except ImportError:
    multipart = None

import pytest

from mini_framework import Application, Router
from mini_framework.responses import PlainTextResponse
from mini_framework.routes.manager import SkipRoute, UNHANDLED
from mini_framework.routes.route import CallableObject

METHODS: list[str] = [
    method for method in HTTPMethod if method != HTTPMethod.CONNECT
]


@pytest.mark.parametrize(
    "path, method, contextmanager",
    [
        (
            "/",
            HTTPMethod.GET,
            nullcontext(),
        ),
        (
            "wrong_path/",
            HTTPMethod.GET,
            pytest.raises(
                ValueError, match="Path 'wrong_path/' must start with '/'"
            ),
        ),
        (
            "/wrong_path",
            HTTPMethod.GET,
            pytest.raises(
                ValueError, match="Path '/wrong_path' must end with '/'"
            ),
        ),
        (
            "/",
            "WRONG",
            pytest.raises(
                ValueError, match="Method 'WRONG' is not valid HTTP method"
            ),
        ),
    ],
)
def test_create_route(
    path: str, method: str, contextmanager: AbstractContextManager
) -> None:
    with contextmanager:
        Route(callback=lambda: None, path=path, method=method)


@pytest.mark.parametrize(
    "callback, expected_prepared_kwargs",
    [
        (lambda: None, {}),
        (lambda a: None, {"a": 1}),
        (lambda c: None, {}),
        (lambda **kwargs: None, {"a": 1, "b": 2}),
    ],
)
def test_prepare_kwargs(
    callback: Callable[..., None], expected_prepared_kwargs: dict[str, str]
) -> None:
    kwargs = {"a": 1, "b": 2}

    route = CallableObject(callback=callback)

    prepared_kwargs = route._prepare_kwargs(kwargs)

    assert prepared_kwargs == expected_prepared_kwargs


@pytest.mark.parametrize("method", METHODS)
def test_register_route_with_specified_method(
    app: Application, method: str, mock_request: Mock
) -> None:
    mocked_callback = Mock(return_value=None)
    app.route.register(mocked_callback, "/", method=method)
    mock_request.method = method

    app.propagate(mock_request)

    mocked_callback.assert_called_once()


@pytest.mark.parametrize(
    "method, route",
    [(method, getattr(Router, method.lower())) for method in METHODS],
)
def test_register_route_with_dynamic_route(
    app: Application, mock_request: Mock, method: str, route: Callable
) -> None:
    mocked_callback = Mock(return_value=None)
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

    assert response.content == "Hello, World!"


def test_not_registered_route(app: Application, mock_request: Mock) -> None:
    response = app.propagate(mock_request)

    assert response is UNHANDLED


def test_successful_route_resolution(
    app: Application, mock_request: Mock
) -> None:
    mocked_callback = Mock(return_value=None)

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
    mocked_callback = Mock(return_value=None)

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
    def index():
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

    router1.get("/")(lambda: True)

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

    assert response.content == "first"
    mocked_filter.assert_not_called()


def test_resolve_upload_file_params_no_content_type_header_given_error(
    mock_request: Mock,
) -> None:
    mock_request.form.side_effect = ValueError("No Content-Type header given!")
    route = Route(callback=lambda: None, path="/", method=HTTPMethod.GET)
    route.upload_files = ["upload_file"]
    params = {}

    resolve_upload_file_params(route, mock_request, params=params)

    assert params == {}


def test_resolve_upload_file_params_unexpected_error_message(
    mock_request: Mock,
) -> None:
    mock_request.form.side_effect = ValueError("Hello, World!")
    route = Route(callback=lambda: None, path="/", method=HTTPMethod.GET)
    route.upload_files = ["upload_file"]
    params = {}

    with pytest.raises(ValueError, match="Hello, World!"):
        resolve_upload_file_params(route, mock_request, params=params)


def test_resolve_upload_file_params_no_files_specified(
    mock_request: Mock,
) -> None:
    mock_request.form.return_value = FormData(fields=[], files=[])
    route = Route(callback=lambda: None, path="/", method=HTTPMethod.GET)
    route.upload_files = ["upload_file"]
    params = {}

    resolve_upload_file_params(route, mock_request, params=params)

    assert params == {}


def test_resolve_upload_file_params_missing_one_file(
    mock_request: Mock,
) -> None:
    file = create_autospec(File)

    mock_request.form.return_value = FormData(fields=[], files=[file])

    route = Route(callback=lambda: None, path="/", method=HTTPMethod.GET)
    route.upload_files = ["upload_file_1", "upload_file_2"]
    params = {}

    resolve_upload_file_params(route, mock_request, params=params)

    assert len(params) == 1
    assert isinstance(params["upload_file_1"], UploadFile)
    assert params["upload_file_1"].file is file.file_object
