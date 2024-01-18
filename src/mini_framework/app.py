from collections.abc import Iterator
from http import HTTPStatus
from typing import Any

from mini_framework.errors.handlers import http_exception_handler
from mini_framework.exceptions import HTTPException
from mini_framework.filters.exception import ExceptionTypeFilter
from mini_framework.middlewares.errors import ErrorsMiddleware
from mini_framework.responses import PlainTextResponse, Response
from mini_framework.router import Router
from mini_framework.routes.manager import UNHANDLED
from mini_framework.utils import get_status_code_and_phrase, prepare_headers


class Application(Router):
    __slots__ = ("_workflow_data",)

    def __init__(
        self,
        *,
        name: str = "Application",
        **kwargs: Any,
    ) -> None:
        super().__init__(name=name)
        self._workflow_data: dict[str, Any] = kwargs

        self.route.outer_middleware.register(ErrorsMiddleware(self))
        self.error.register(
            http_exception_handler,
            ExceptionTypeFilter(HTTPException),
        )

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
            "Application can not be attached to another Router.",
        )

    def __call__(self, environ, start_response) -> list[bytes]:
        path: str = environ["PATH_INFO"]

        if not path.endswith("/"):
            path += "/"

        method: str = environ["REQUEST_METHOD"]

        data: dict[str, Any] = {}

        response = self.propagate(path, method=method, data=data)

        if response is UNHANDLED:
            response = PlainTextResponse(
                content=HTTPStatus.NOT_FOUND.phrase,
                status_code=HTTPStatus.NOT_FOUND,
            )
            status = get_status_code_and_phrase(response.status_code)
            content = response.render()
            headers = prepare_headers(response, content=content)
            start_response(status, headers)
            return [content]

        status = get_status_code_and_phrase(response.status_code)
        content = response.render()
        headers = prepare_headers(response, content=content)
        start_response(status, headers)
        return [content]

    def propagate(
        self,
        path: str,
        /,
        *,
        method: str,
        data: dict[str, Any] | None = None,
    ) -> Response:
        if data is None:
            data = {}

        data.update(self._workflow_data, path=path, method=method)

        for router in self._get_routers(path, method=method):
            for tail_router in router.chain_tail:
                response = self.route.wrap_outer_middleware(
                    tail_router.route.trigger,
                    data,
                )
                if response is not UNHANDLED:
                    return response

        return UNHANDLED

    def _get_routers(self, path: str, /, *, method: str) -> Iterator[Router]:
        for router in self.chain_tail:
            for route in router.route:
                if route.path == path and route.method == method:
                    yield router

    def propagate_error(
        self,
        exception: Exception,
        data: dict[str, Any],
    ) -> Response:
        data.update(self._workflow_data, exception=exception)

        for tail_router in self.chain_tail:
            response = self.error.wrap_outer_middleware(
                tail_router.error.trigger,
                data,
            )
            if response is not UNHANDLED:
                return response

        return UNHANDLED
