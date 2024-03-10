import json
from collections.abc import Iterable, Callable
from typing import Any
from wsgiref.types import StartResponse, WSGIEnvironment

from mini_framework.staticfiles import NOT_FOUND_RESPONSE
from mini_framework.validators.base import Validator
from mini_framework.middlewares.errors import ErrorsMiddleware
from mini_framework.request import (
    extract_path_params,
    Request,
    ensure_trailing_slash,
)
from mini_framework.responses import (
    get_status_code_and_phrase,
    prepare_headers,
    Response,
    StreamingResponse,
    FileResponse,
    JSONResponse,
)
from mini_framework.router import Router
from mini_framework.routes.manager import UNHANDLED
from mini_framework.routes.route import Route
from mini_framework.validators.pydantic import PydanticValidator


class Application(Router):
    __slots__ = ("_workflow_data", "_validator", "_json_loads")

    def __init__(
        self,
        *,
        name: str = "Application",
        prefix: str = "",
        default_response_class: type[Response] = JSONResponse,
        validator: Validator = PydanticValidator(),
        json_loads: Callable[..., Any] = json.loads,
        **kwargs: Any,
    ) -> None:
        super().__init__(
            name=name,
            prefix=prefix,
            default_response_class=default_response_class,
        )
        self._workflow_data: dict[str, Any] = kwargs
        self._validator = validator
        self._json_loads = json_loads

        self.route.outer_middleware.register(ErrorsMiddleware())

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
        raise RuntimeError("Application can not be attached to another Router")

    def __call__(
        self, environ: WSGIEnvironment, start_response: StartResponse
    ) -> Iterable[bytes]:
        path = ensure_trailing_slash(environ["PATH_INFO"])

        path_template: str | None = self._get_path_template(path)

        if path_template is None:
            response = NOT_FOUND_RESPONSE
        else:
            path_params = extract_path_params(path_template, path)

            request = Request(
                self,
                environ,
                path_params=path_params,
                json_loads=self._json_loads,
            )

            response = self.propagate(request)

            if response is UNHANDLED:
                response = NOT_FOUND_RESPONSE

        status = get_status_code_and_phrase(response.status_code)
        body = response.render()
        headers = prepare_headers(response, body)
        start_response(status, headers)
        if isinstance(response, StreamingResponse):
            return response.body_iterator
        elif isinstance(response, FileResponse):
            return response.iter_content()
        return (body,)

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
        for router, route in self._get_matching_routers_and_routes(request):
            if route.response_class is None:
                response_obj = router.default_response_class(
                    content=None, status_code=route.status_code
                )
            else:
                response_obj = route.response_class(
                    content=None, status_code=route.status_code
                )

            response = self.route.wrap_outer_middleware(
                router.route.trigger,
                {
                    **self._workflow_data,
                    **kwargs,
                    "app": self,
                    "router": router,
                    "route": route,
                    "request": request,
                    "response": response_obj,
                    "validator": self._validator,
                },
            )

            if response is UNHANDLED:
                continue

            if not isinstance(response, Response):
                response_obj.content = response
                return response_obj

            return response

        return UNHANDLED

    def _get_matching_routers_and_routes(
        self,
        request: Request,
        /,  # noqa: W504
    ) -> Iterable[tuple[Router, Route]]:
        for router in self.chain_tail:
            for route in router.route:
                if route.match(request):
                    yield router, route

    def propagate_error(
        self, exception: Exception, /, **kwargs: Any
    ) -> Response:
        for router in self.chain_tail:
            response = self.error.wrap_outer_middleware(
                router.error.trigger,
                {
                    **self._workflow_data,
                    **kwargs,
                    "app": self,
                    "router": router,
                    "exception": exception,
                },
            )
            if response is not UNHANDLED:
                return response

        return UNHANDLED
