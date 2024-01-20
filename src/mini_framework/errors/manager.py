from __future__ import annotations

from collections.abc import Callable, Iterator
from typing import Any, TYPE_CHECKING

from mini_framework.errors.error import Error
from mini_framework.errors.handlers import http_exception_handler
from mini_framework.exceptions import HTTPException
from mini_framework.filters.exception import ExceptionTypeFilter
from mini_framework.middlewares.base import Middleware
from mini_framework.middlewares.manager import MiddlewareManager
from mini_framework.routes.manager import SkipRoute, UNHANDLED
from mini_framework.routes.route import Callback, Filter

if TYPE_CHECKING:
    from mini_framework.router import Router


class ErrorsManager:
    __slots__ = (
        "_router",
        "_errors",
        "outer_middleware",
        "middleware",
        "_error",
        "_http_exception_error",
    )

    def __init__(self, router: Router) -> None:
        self._router = router
        self._errors: list[Error] = []

        self.outer_middleware = MiddlewareManager()
        self.middleware = MiddlewareManager()

        # This error is used to check root filters
        self._error = Error(callback=lambda: True)
        self._http_exception_error = Error(
            callback=http_exception_handler,
            filters=[ExceptionTypeFilter(HTTPException)],
        )

    def __iter__(self) -> Iterator[Error]:
        return iter(self._errors)

    def wrap_outer_middleware(
        self, callback: Any, data: dict[str, Any]
    ) -> Any:
        wrapped_outer = self.outer_middleware.wrap_middlewares(
            self.outer_middleware, callback
        )
        return wrapped_outer(data)

    def filter(self, *filters: Filter) -> None:
        self._error.filters.extend(filters)

    def check_root_filters(
        self, data: dict[str, Any]
    ) -> tuple[bool, dict[str, Any]]:
        return self._error.check(data)

    def trigger(self, **kwargs: Any) -> Any:
        for head_router in reversed(tuple(self._router.chain_head)):
            result, data = head_router.error.check_root_filters(kwargs)
            if not result:
                return UNHANDLED
            kwargs.update(data)

        errors = self._errors + [self._http_exception_error]

        for error in errors:
            kwargs["error"] = error
            result, data = error.check(kwargs)

            if result:
                kwargs.update(data)
                try:
                    wrapped_inner = self.middleware.wrap_middlewares(
                        self._resolve_middlewares(),  # noqa: B038
                        error.callback,
                    )
                    return wrapped_inner(kwargs)
                except SkipRoute:
                    continue

        return UNHANDLED

    def _resolve_middlewares(self) -> list[Middleware]:
        middlewares: list[Middleware] = []
        for router in reversed(tuple(self._router.chain_head)):
            middlewares.extend(tuple(router.error.middleware))
        return middlewares

    def __call__(self, *filters: Filter) -> Callable[[Callback], Callback]:
        def wrapper(callback: Callback) -> Callback:
            self.register(callback, *filters)
            return callback

        return wrapper

    def register(self, callback: Callback, /, *filters: Filter) -> Callback:
        self._errors.append(Error(callback=callback, filters=list(filters)))
        return callback
