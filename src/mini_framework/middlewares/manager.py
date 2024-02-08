from collections.abc import Callable, Iterable, Iterator
from functools import partial, wraps
from typing import Any

from mini_framework.middlewares.base import CallNext, Middleware
from mini_framework.routes.route import CallbackType


class MiddlewareManager:
    __slots__ = ("_middlewares",)

    def __init__(self) -> None:
        self._middlewares: list[Middleware] = []

    def __iter__(self) -> Iterator[Middleware]:
        return iter(self._middlewares)

    def __call__(
        self, middleware: Middleware | None = None
    ) -> Callable[[Middleware], Middleware] | Middleware:
        if middleware is None:
            return self.register
        return self.register(middleware)

    def register(self, middleware: Middleware) -> Middleware:
        self._middlewares.append(middleware)
        return middleware

    @staticmethod
    def wrap_middlewares(
        middlewares: Iterable[Middleware], callback: CallbackType
    ) -> CallNext:
        @wraps(callback)
        def callback_wrapper(kwargs: dict[str, Any]) -> Any:
            return callback(**kwargs)

        middleware = callback_wrapper
        for m in reversed(tuple(middlewares)):
            middleware = partial(m, middleware)
        return middleware
