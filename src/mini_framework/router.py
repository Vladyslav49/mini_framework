from collections.abc import Iterator
from http import HTTPMethod
from typing import Callable, Optional

from mini_framework.route import Handler, Route


class Router:
    __slots__ = ("_routes", "_name", "_parent_router", "_sub_routers")

    def __init__(self, *, name: str | None = None) -> None:
        self._routes: list[Route] = []
        self._name = name or hex(id(self))
        self._parent_router: Router | None = None
        self._sub_routers: list[Router] = []

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

        parent: Optional[Router] = router
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
    def chain_tail(self) -> Iterator["Router"]:
        yield self
        for router in self._sub_routers:
            yield from router.chain_tail

    def __str__(self) -> str:
        return f"{type(self).__name__} {self.name!r}"

    def __repr__(self) -> str:
        return f"<{self}>"

    def get(
        self,
        path: str,
        /,
        *,
        status_code: int = 200,
    ) -> Callable[[Handler], None]:
        return self.route(
            path,
            method=HTTPMethod.GET,
            status_code=status_code,
        )

    def post(
        self,
        path: str,
        /,
        *,
        status_code: int = 200,
    ) -> Callable[[Handler], None]:
        return self.route(
            path,
            method=HTTPMethod.POST,
            status_code=status_code,
        )

    def put(
        self,
        path: str,
        /,
        *,
        status_code: int = 200,
    ) -> Callable[[Handler], None]:
        return self.route(
            path,
            method=HTTPMethod.PUT,
            status_code=status_code,
        )

    def patch(
        self,
        path: str,
        /,
        *,
        status_code: int = 200,
    ) -> Callable[[Handler], None]:
        return self.route(
            path,
            method=HTTPMethod.PATCH,
            status_code=status_code,
        )

    def delete(
        self,
        path: str,
        /,
        *,
        status_code: int = 200,
    ) -> Callable[[Handler], None]:
        return self.route(
            path,
            method=HTTPMethod.DELETE,
            status_code=status_code,
        )

    def route(
        self,
        path: str,
        /,
        *,
        method: HTTPMethod | str,
        status_code: int = 200,
    ) -> Callable[[Handler], None]:
        def wrapper(handler: Handler) -> None:
            if self._get_route(path, method) is not None:
                raise ValueError(
                    f"Route for path {path!r} and method {str(method)!r} already exists",  # noqa: E501
                )

            self._routes.append(
                Route(
                    handler=handler,
                    path=path,
                    method=method,
                    status_code=status_code,
                ),
            )

        return wrapper

    def _get_route(
        self,
        path: str,
        method: HTTPMethod | str,
        /,
    ) -> Route | None:
        """Return route for path and method if exists, otherwise None."""
        for router in self.chain_tail:
            for route in router._routes:
                if route.path == path and route.method == method:
                    return route
        return None
