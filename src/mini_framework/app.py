from http import HTTPStatus
from typing import Any

from mini_framework.responses import PlainTextResponse, Response
from mini_framework.router import Router
from mini_framework.utils import get_status_code_and_phrase, prepare_headers


class Application(Router):
    __slots__ = ("_routes", "_default_response_class")

    def __init__(
        self,
        *,
        name: str = "Application",
        default_response_class: type[Response] = PlainTextResponse,
    ) -> None:
        super().__init__(name=name)
        self._default_response_class = default_response_class

    @property
    def parent_router(self) -> Router | None:
        return None

    @parent_router.setter
    def parent_router(self, router: Router) -> None:
        raise RuntimeError(
            "Application can not be attached to another Router.",
        )

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
            status = get_status_code_and_phrase(response.status_code)
            content = response.render()
            headers = prepare_headers(response, content=content)
            start_response(status, headers)
            return [content]

        response: Any = route.handler()

        if not isinstance(response, Response):
            response = self._default_response_class(
                content=response,
                status_code=route.status_code,
            )

        status = get_status_code_and_phrase(response.status_code)
        content = response.render()
        headers = prepare_headers(response, content=content)
        start_response(status, headers)
        return [content]
