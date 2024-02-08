from collections.abc import Iterator
from http import HTTPStatus
from typing import Any, Final
from wsgiref.types import StartResponse, WSGIEnvironment

from mini_framework.middlewares.errors import ErrorsMiddleware
from mini_framework.request import extract_path_params, Request, prepare_path
from mini_framework.responses import (
    get_status_code_and_phrase,
    PlainTextResponse,
    prepare_headers,
    Response,
)
from mini_framework.router import Router
from mini_framework.routes.manager import UNHANDLED
from mini_framework.routes.route import Route

_NOT_FOUND_RESPONSE: Final[PlainTextResponse] = PlainTextResponse(
    HTTPStatus.NOT_FOUND.phrase, status_code=HTTPStatus.NOT_FOUND
)


class Application(Router):
    __slots__ = ("_workflow_data",)

    def __init__(self, *, name: str = "Application", **kwargs: Any) -> None:
        super().__init__(name=name)
        self._workflow_data: dict[str, Any] = kwargs

        self.route.outer_middleware.register(ErrorsMiddleware(self))

    def __getitem__(self, key: str) -> Any:
        return self._workflow_data[key]

    def __setitem__(self, key: str, value: Any) -> None:
        self._workflow_data[key] = value

    def __delitem__(self, key: str) -> None:
        del self._workflow_data[key]

    @property
    def parent_router(self) -> Router | None:
        return None

    @parent_router.setter
    def parent_router(self, router: Router) -> None:
        raise RuntimeError(
            "Application can not be attached to another Router."
        )

    def __call__(
        self, environ: WSGIEnvironment, start_response: StartResponse
    ) -> list[bytes]:
        path = prepare_path(environ["PATH_INFO"])

        path_template: str | None = self._get_path_template(path)

        if path_template is None:
            response = _NOT_FOUND_RESPONSE
        else:
            path_params = extract_path_params(path_template, path)

            request = Request(environ, path_params=path_params)

            response = self.propagate(request, **path_params)

            if response is UNHANDLED:
                response = _NOT_FOUND_RESPONSE

        status = get_status_code_and_phrase(response.status_code)
        headers = prepare_headers(response)
        start_response(status, headers)
        return [response.body]

    def _get_path_template(self, path: str) -> str | None:
        for router in self.chain_tail:
            for route in router.route:
                if route.path == path:
                    return route.path
                try:
                    path_params = extract_path_params(route.path, path)
                except ValueError:
                    continue
                if path_params:
                    return route.path
        return None

    def propagate(self, request: Request, /, **kwargs: Any) -> Response:
        for router, route in self._get_routers_and_routes(request):
            for tail_router in router.chain_tail:
                response = self.route.wrap_outer_middleware(
                    tail_router.route.trigger,
                    {
                        **self._workflow_data,
                        **kwargs,
                        "request": request,
                        "route": route,
                    },
                )
                if response is not UNHANDLED:
                    return response

        return UNHANDLED

    def _get_routers_and_routes(
        self,
        request: Request,
        /,  # noqa: W504
    ) -> Iterator[tuple[Router, Route]]:
        for router in self.chain_tail:
            for route in router.route:
                if route.match(request):
                    yield router, route

    def propagate_error(
        self, exception: Exception, /, **kwargs: Any
    ) -> Response:
        for tail_router in self.chain_tail:
            response = self.error.wrap_outer_middleware(
                tail_router.error.trigger,
                {
                    **self._workflow_data,
                    **kwargs,
                    "exception": exception,
                },
            )
            if response is not UNHANDLED:
                return response

        return UNHANDLED
