from __future__ import annotations

from collections.abc import Callable, Iterator
from http import HTTPMethod, HTTPStatus
from typing import Any, TYPE_CHECKING
from unittest.mock import sentinel

from mini_framework.validators.base import Validator
from mini_framework.request import Request
from mini_framework.middlewares.base import Middleware
from mini_framework.middlewares.manager import MiddlewareManager
from mini_framework.responses import Response
from mini_framework.routes.route import Route
from mini_framework.routes.route import CallableObject, CallbackType

if TYPE_CHECKING:
    from mini_framework.router import Router

UNHANDLED = sentinel.UNHANDLED


class SkipRoute(Exception):
    pass


class RoutesManager:
    __slots__ = (
        "_router",
        "_routes",
        "outer_middleware",
        "middleware",
        "_route",
    )

    def __init__(self, router: Router) -> None:
        self._router = router
        self._routes: list[Route] = []

        self.outer_middleware = MiddlewareManager()
        self.middleware = MiddlewareManager()

        # This route is used to check root filters
        self._route = Route(
            callback=lambda: True, path="/", method=HTTPMethod.GET
        )

    def __iter__(self) -> Iterator[Route]:
        return iter(self._routes)

    def wrap_outer_middleware(
        self, callback: Any, data: dict[str, Any]
    ) -> Any:
        wrapped_outer = self.middleware.wrap_middlewares(
            self.outer_middleware,
            callback,
        )
        return wrapped_outer(data)

    def filter(self, *filters: CallbackType) -> None:
        self._route.filters.extend(
            [CallableObject(callback=filter) for filter in filters],
        )

    def check_root_filters(self, **kwargs: Any) -> tuple[bool, dict[str, Any]]:
        return self._route.check(**kwargs)

    def trigger(self, __validator__: Validator, **kwargs: Any) -> Any:
        for head_router in reversed(tuple(self._router.chain_head)):
            result, data = head_router.route.check_root_filters(**kwargs)
            if not result:
                return UNHANDLED
            kwargs.update(data)

        route: Route = kwargs["route"]

        result, data = route.check(**kwargs)

        if result:
            kwargs.update(data)

            request: Request = kwargs["request"]

            params = route.validate_params(request, __validator__)

            kwargs.update(params)

            try:
                wrapped_inner = self.middleware.wrap_middlewares(
                    self._resolve_middlewares(),  # noqa: B038
                    route.call,
                )
                response = wrapped_inner(kwargs)
            except SkipRoute:
                return UNHANDLED
            else:
                return_type = (
                    route.response_model
                    if route.response_model is not None
                    else route.return_annotation
                )
                obj = __validator__.validate_response(response, return_type)
                return __validator__.serialize_response(obj, return_type)

        return UNHANDLED

    def _resolve_middlewares(self) -> list[Middleware]:
        middlewares: list[Middleware] = []
        for router in reversed(tuple(self._router.chain_head)):
            middlewares.extend(tuple(router.route.middleware))
        return middlewares

    def __call__(
        self,
        path: str,
        /,
        *filters: CallbackType,
        method: str,
        status_code: int = HTTPStatus.OK,
        response_class: type[Response] | None = None,
        response_model: type | None = None,
    ) -> Callable[[CallbackType], CallbackType]:
        def wrapper(callback: CallbackType) -> CallbackType:
            self.register(
                callback,
                path,
                *filters,
                method=method,
                status_code=status_code,
                response_class=response_class,
                response_model=response_model,
            )
            return callback

        return wrapper

    def register(
        self,
        callback: CallbackType,
        path: str,
        /,
        *filters: CallbackType,
        method: str,
        status_code: int = HTTPStatus.OK,
        response_class: type[Response] | None = None,
        response_model: type | None = None,
    ) -> CallbackType:
        self._routes.append(
            Route(
                callback=callback,
                path=self._router.prefix + path,
                method=method,
                filters=[
                    CallableObject(callback=filter) for filter in filters
                ],
                status_code=status_code,
                response_class=response_class,
                response_model=response_model,
            )
        )
        return callback
