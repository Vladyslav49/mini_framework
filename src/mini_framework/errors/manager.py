from __future__ import annotations

from collections.abc import Callable, Iterator
from typing import Any, TYPE_CHECKING

from mini_framework.errors.handlers import (
    http_exception_handler,
    request_validation_error_handler,
)
from mini_framework.exceptions import HTTPException, RequestValidationError
from mini_framework.filters.exception import ExceptionTypeFilter
from mini_framework.middlewares.base import Middleware
from mini_framework.middlewares.manager import MiddlewareManager
from mini_framework.routes.manager import SkipRoute, UNHANDLED
from mini_framework.routes.route import (
    CallableObject,
    CallbackType,
    HandlerObject,
)

if TYPE_CHECKING:
    from mini_framework.router import Router


class ErrorsManager:
    __slots__ = (
        "_router",
        "_handlers",
        "outer_middleware",
        "middleware",
        "_handler",
        "_http_exception_error",
        "_request_validation_error",
    )

    def __init__(self, router: Router) -> None:
        self._router = router
        self._handlers: list[HandlerObject] = []

        self.outer_middleware = MiddlewareManager()
        self.middleware = MiddlewareManager()

        self._http_exception_error = HandlerObject(
            callback=http_exception_handler,
            filters=[
                CallableObject(callback=ExceptionTypeFilter(HTTPException)),
            ],
        )
        self._request_validation_error = HandlerObject(
            callback=request_validation_error_handler,
            filters=[
                CallableObject(
                    callback=ExceptionTypeFilter(RequestValidationError)
                ),
            ],
        )

        # This handler is used to check root filters
        self._handler = HandlerObject(callback=lambda: True)

    def __iter__(self) -> Iterator[HandlerObject]:
        return iter(self._handlers)

    def wrap_outer_middleware(
        self, callback: Any, data: dict[str, Any]
    ) -> Any:
        wrapped_outer = self.outer_middleware.wrap_middlewares(
            self.outer_middleware,
            callback,
        )
        return wrapped_outer(data)

    def filter(self, *filters: CallbackType) -> None:
        self._handler.filters.extend(
            [CallableObject(callback=filter) for filter in filters]
        )

    def check_root_filters(
        self, kwargs: dict[str, Any]
    ) -> tuple[bool, dict[str, Any]]:
        return self._handler.check(**kwargs)

    def trigger(self, **kwargs: Any) -> Any:
        for head_router in reversed(tuple(self._router.chain_head)):
            result, data = head_router.error.check_root_filters(kwargs)
            if not result:
                return UNHANDLED
            kwargs.update(data)

        errors = self._handlers + [
            self._http_exception_error,
            self._request_validation_error,
        ]

        for error in errors:
            kwargs["error"] = error
            result, data = error.check(**kwargs)

            if result:
                kwargs.update(data)
                try:
                    wrapped_inner = self.middleware.wrap_middlewares(
                        self._resolve_middlewares(),  # noqa: B038
                        error.call,
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

    def __call__(
        self, *filters: CallbackType
    ) -> Callable[[CallbackType], CallbackType]:
        def wrapper(callback: CallbackType) -> CallbackType:
            self.register(callback, *filters)
            return callback

        return wrapper

    def register(
        self, callback: CallbackType, /, *filters: CallbackType
    ) -> CallbackType:
        self._handlers.append(
            HandlerObject(
                callback=callback,
                filters=[
                    CallableObject(callback=filter) for filter in filters
                ],
            ),
        )
        return callback
