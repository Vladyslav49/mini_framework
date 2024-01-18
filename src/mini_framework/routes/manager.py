from __future__ import annotations

from collections.abc import Callable, Iterator
from http import HTTPMethod
from typing import Any, TYPE_CHECKING
from unittest.mock import sentinel

from mini_framework.middlewares.base import Middleware
from mini_framework.middlewares.manager import MiddlewareManager
from mini_framework.routes.route import Callback, Filter, Route

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
            callback=lambda: True,
            path="/",
            method=HTTPMethod.GET,
        )

    def __iter__(self) -> Iterator[Route]:
        return iter(self._routes)

    def wrap_outer_middleware(
        self,
        callback: Any,
        data: dict[str, Any],
    ) -> Any:
        wrapped_outer = self.outer_middleware.wrap_middlewares(
            self.outer_middleware,
            callback,
        )
        return wrapped_outer(data)

    def filter(self, *filters: Filter) -> None:
        self._route.filters.extend(filters)

    def check_root_filters(
        self,
        data: dict[str, Any],
    ) -> tuple[bool, dict[str, Any]]:
        return self._route.check(data)

    def trigger(
        self,
        path: str,
        method: str,
        **kwargs: Any,
    ) -> Any:
        for head_router in reversed(tuple(self._router.chain_head)):
            result, data = head_router.route.check_root_filters(kwargs)
            if not result:
                return UNHANDLED
            kwargs.update(data)

        for route in self:
            if route.path == path and route.method == method:
                kwargs["route"] = route
                result, data = route.check(kwargs)

                if result:
                    kwargs.update(data)
                    try:
                        wrapped_inner = self.middleware.wrap_middlewares(
                            self._resolve_middlewares(),  # noqa: B038
                            route.callback,
                        )
                        return wrapped_inner(kwargs)
                    except SkipRoute:
                        continue

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
        *filters: Filter,
        method: str,
    ) -> Callable[[Callback], Callback]:
        def wrapper(callback: Callback) -> Callback:
            self.register(
                callback,
                path,
                *filters,
                method=method,
            )
            return callback

        return wrapper

    def register(
        self,
        callback: Callback,
        path: str,
        /,
        *filters: Filter,
        method: str,
    ) -> Callback:
        self._routes.append(
            Route(
                callback=callback,
                path=path,
                method=method,
                filters=list(filters),
            ),
        )
        return callback