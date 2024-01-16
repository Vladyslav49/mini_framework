from collections.abc import Callable
from http import HTTPMethod, HTTPStatus
from http.client import responses
from typing import Any

from mini_framework.responses import PlainTextResponse, Response
from mini_framework.route import Route


class Application:
    __slots__ = ("_routes", "_default_response_class")

    def __init__(
        self,
        *,
        default_response_class: type[Response] = PlainTextResponse,
    ) -> None:
        self._routes: list[Route] = []
        self._default_response_class = default_response_class

    def __call__(self, environ, start_response) -> list[bytes]:
        path: str = environ["PATH_INFO"]

        if not path.endswith("/"):
            path += "/"

        method: str = environ["REQUEST_METHOD"]

        route = self._get_route(path, method)

        if route is None:
            response = PlainTextResponse(
                content="Not Found",
                status_code=HTTPStatus.NOT_FOUND,
            )
            status = _get_status_code_phrase(response.status_code)
            content = response.render()
            headers = _prepare_headers(response, content=content)
            start_response(status, headers)
            return [content]

        response: Any = route.handler()

        if not isinstance(response, Response):
            response = self._default_response_class(
                content=response,
                status_code=route.status_code,
            )

        status = _get_status_code_phrase(response.status_code)
        content = response.render()
        headers = _prepare_headers(response, content=content)
        start_response(status, headers)
        return [content]

    def _get_route(
        self,
        path: str,
        method: HTTPMethod | str,
        /,
    ) -> Route | None:
        for route in self._routes:
            if route.path == path and route.method == method:
                return route
        return None

    def get(
        self,
        path: str,
        /,
        *,
        status_code: int = 200,
    ) -> Callable[[Callable[[], Any]], None]:
        return self.route(
            path,
            method=HTTPMethod.GET,
            status_code=status_code,
        )

    def post(
        self,
        path: str,
        /,
        *,
        status_code: int = 200,
    ) -> Callable[[Callable[[], Any]], None]:
        return self.route(
            path,
            method=HTTPMethod.POST,
            status_code=status_code,
        )

    def put(
        self,
        path: str,
        /,
        *,
        status_code: int = 200,
    ) -> Callable[[Callable[[], Any]], None]:
        return self.route(
            path,
            method=HTTPMethod.PUT,
            status_code=status_code,
        )

    def patch(
        self,
        path: str,
        /,
        *,
        status_code: int = 200,
    ) -> Callable[[Callable[[], Any]], None]:
        return self.route(
            path,
            method=HTTPMethod.PATCH,
            status_code=status_code,
        )

    def delete(
        self,
        path: str,
        /,
        *,
        status_code: int = 200,
    ) -> Callable[[Callable[[], Any]], None]:
        return self.route(
            path,
            method=HTTPMethod.DELETE,
            status_code=status_code,
        )

    def route(
        self,
        path: str,
        /,
        *,
        method: HTTPMethod | str,
        status_code: int = 200,
    ) -> Callable[[Callable[[], Any]], None]:
        def wrapper(route: Callable[[], Any]) -> None:
            if self._get_route(path, method) is not None:
                raise ValueError(
                    f"Route for path {path!r} and method {str(method)!r} already exists",  # noqa: E501
                )

            self._routes.append(
                Route(
                    handler=route,
                    path=path,
                    method=method,
                    status_code=status_code,
                ),
            )

        return wrapper


def _get_status_code_phrase(status_code: int) -> str:
    return f"{status_code} {responses[status_code]}"


def _prepare_headers(
    response: Response,
    *,
    content: Any,
) -> list[tuple[str, str]]:
    headers = [
        ("Content-Type", response.media_type),
        ("Content-Length", str(len(content))),
    ] + list(response.headers.items())
    return headers
