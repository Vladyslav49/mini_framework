from collections.abc import Iterator
from http import HTTPMethod, HTTPStatus
from typing import Callable, Optional

from mini_framework.filters import BaseFilter
from mini_framework.managers.routes import RoutesManager
from mini_framework.route import Callback


class Router:
    __slots__ = ("_name", "_parent_router", "_sub_routers", "routes")

    def __init__(self, *, name: str | None = None) -> None:
        self._name = name or hex(id(self))
        self._parent_router: Router | None = None
        self._sub_routers: list[Router] = []

        self.routes: RoutesManager = RoutesManager()

    @property
    def name(self) -> str:
        return self._name

    @property
    def parent_router(self) -> Optional["Router"]:
        return self._parent_router

    @parent_router.setter
    def parent_router(self, router: "Router") -> None:
        if not isinstance(router, Router):
            raise ValueError(
                f"router should be instance of Router not {type(router).__name__!r}",  # noqa: E501
            )
        if self._parent_router:
            raise RuntimeError(
                f"Router is already attached to {self._parent_router!r}",
            )
        if self is router:
            raise RuntimeError("Self-referencing routers is not allowed")

        parent: Router | None = router
        while parent is not None:
            if parent is self:
                raise RuntimeError(
                    "Circular referencing of Router is not allowed",
                )

            parent = parent.parent_router

        self._parent_router = router
        router._sub_routers.append(self)

    def include_router(self, router: "Router") -> "Router":
        if not isinstance(router, Router):
            raise ValueError(
                f"router should be instance of Router not {type(router).__name__!r}",  # noqa: E501
            )
        router.parent_router = self
        return router

    @property
    def chain_head(self) -> Iterator["Router"]:
        router: Router | None = self
        while router is not None:
            yield router
            router = router.parent_router

    @property
    def chain_tail(self) -> Iterator["Router"]:
        yield self
        for router in self._sub_routers:
            yield from router.chain_tail

    def __str__(self) -> str:
        return f"{type(self).__name__} {self.name!r}"

    def __repr__(self) -> str:
        return f"<{self}>"

    def filter(self, *filters: BaseFilter) -> None:
        self.routes.filter(*filters)

    def connect(
        self,
        path: str,
        /,
        *filters: BaseFilter,
        status_code: int = HTTPStatus.OK,
    ) -> Callable[[Callback], Callback]:
        return self.routes(
            path,
            *filters,
            method=HTTPMethod.CONNECT,
            status_code=status_code,
        )

    def delete(
        self,
        path: str,
        /,
        *filters: BaseFilter,
        status_code: int = HTTPStatus.OK,
    ) -> Callable[[Callback], Callback]:
        return self.routes(
            path,
            *filters,
            method=HTTPMethod.DELETE,
            status_code=status_code,
        )

    def get(
        self,
        path: str,
        /,
        *filters: BaseFilter,
        status_code: int = HTTPStatus.OK,
    ) -> Callable[[Callback], Callback]:
        return self.routes(
            path,
            *filters,
            method=HTTPMethod.GET,
            status_code=status_code,
        )

    def head(
        self,
        path: str,
        /,
        *filters: BaseFilter,
        status_code: int = HTTPStatus.OK,
    ) -> Callable[[Callback], Callback]:
        return self.routes(
            path,
            *filters,
            method=HTTPMethod.HEAD,
            status_code=status_code,
        )

    def options(
        self,
        path: str,
        /,
        *filters: BaseFilter,
        status_code: int = HTTPStatus.OK,
    ) -> Callable[[Callback], Callback]:
        return self.routes(
            path,
            *filters,
            method=HTTPMethod.OPTIONS,
            status_code=status_code,
        )

    def patch(
        self,
        path: str,
        /,
        *filters: BaseFilter,
        status_code: int = HTTPStatus.OK,
    ) -> Callable[[Callback], Callback]:
        return self.routes(
            path,
            *filters,
            method=HTTPMethod.PATCH,
            status_code=status_code,
        )

    def post(
        self,
        path: str,
        /,
        *filters: BaseFilter,
        status_code: int = HTTPStatus.OK,
    ) -> Callable[[Callback], Callback]:
        return self.routes(
            path,
            *filters,
            method=HTTPMethod.POST,
            status_code=status_code,
        )

    def put(
        self,
        path: str,
        /,
        *filters: BaseFilter,
        status_code: int = HTTPStatus.OK,
    ) -> Callable[[Callback], Callback]:
        return self.routes(
            path,
            *filters,
            method=HTTPMethod.PUT,
            status_code=status_code,
        )

    def trace(
        self,
        path: str,
        /,
        *filters: BaseFilter,
        status_code: int = HTTPStatus.OK,
    ) -> Callable[[Callback], Callback]:
        return self.routes(
            path,
            *filters,
            method=HTTPMethod.TRACE,
            status_code=status_code,
        )
