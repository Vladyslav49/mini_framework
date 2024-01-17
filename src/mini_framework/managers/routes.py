from collections.abc import Callable, Iterator
from http import HTTPMethod, HTTPStatus
from typing import Any
from unittest.mock import sentinel

from mini_framework.filters import BaseFilter
from mini_framework.route import Callback, Route

UNHANDLED = sentinel.UNHANDLED


class RoutesManager:
    __slots__ = ("_routes", "_route")

    def __init__(self) -> None:
        self._routes: list[Route] = []

        # This route is used to check root filters
        self._route = Route(
            callback=lambda: True,
            path="/",
            method=HTTPMethod.GET,
        )

    def __iter__(self) -> Iterator[Route]:
        return iter(self._routes)

    def filter(self, *filters: BaseFilter) -> None:
        self._route.filters.extend(filters)

    def check_root_filters(self) -> bool:
        return self._route.check()

    def trigger(self, path: str, /, *, method: str) -> tuple[Any, int | None]:
        for route in self:
            if route.path == path and route.method == method and route.check():
                return route.callback(), route.status_code
        return UNHANDLED, None

    def __call__(
        self,
        path: str,
        /,
        *filters: BaseFilter,
        method: str,
        status_code: int = HTTPStatus.OK,
    ) -> Callable[[Callback], Callback]:
        def wrapper(callback: Callback) -> Callback:
            self.register(
                callback,
                path,
                *filters,
                method=method,
                status_code=status_code,
            )
            return callback

        return wrapper

    def register(
        self,
        callback: Callback,
        path: str,
        /,
        *filters: BaseFilter,
        method: str,
        status_code: int = HTTPStatus.OK,
    ) -> Callback:
        self._routes.append(
            Route(
                callback=callback,
                path=path,
                method=method,
                status_code=status_code,
                filters=list(filters),
            ),
        )
        return callback
