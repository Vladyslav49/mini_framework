from __future__ import annotations

from collections.abc import Callable, Iterable, Sequence
from http import HTTPMethod, HTTPStatus
from os import PathLike
from pathlib import Path
from typing import Any, Final

from mini_framework.request import Request
from mini_framework.errors.manager import ErrorsManager
from mini_framework.middlewares.base import Middleware
from mini_framework.responses import Response, JSONResponse, FileResponse
from mini_framework.routes.manager import RoutesManager
from mini_framework.routes.route import CallbackType, NoMatchFound
from mini_framework.staticfiles import is_not_modified

NOT_FOUND_RESPONSE: Final[JSONResponse] = JSONResponse(
    {"detail": HTTPStatus.NOT_FOUND.phrase},
    status_code=HTTPStatus.NOT_FOUND,
)
NOT_MODIFIED_RESPONSE: Final[Response] = Response(
    content=None, status_code=HTTPStatus.NOT_MODIFIED
)


class Router:
    __slots__ = (
        "_name",
        "_prefix",
        "default_response_class",
        "_parent_router",
        "_sub_routers",
        "route",
        "errors",
        "error",
    )

    def __init__(
        self,
        *,
        name: str | None = None,
        prefix: str = "",
        default_response_class: type[Response] = JSONResponse,
    ) -> None:
        self._name = name or hex(id(self))
        self.prefix = prefix
        self.default_response_class = default_response_class

        self._parent_router: Router | None = None
        self._sub_routers: list[Router] = []

        self.route = RoutesManager(self)
        self.errors = self.error = ErrorsManager(self)

    @property
    def name(self) -> str:
        return self._name

    @property
    def prefix(self) -> str:
        return self._prefix

    @prefix.setter
    def prefix(self, prefix: str) -> None:
        if prefix and not prefix.startswith("/"):
            raise ValueError(f"Prefix {prefix!r} must start with '/'")
        if prefix.endswith("/"):
            raise ValueError(f"Prefix {prefix!r} must not end with '/'")
        self._prefix = prefix

    @property
    def parent_router(self) -> Router | None:
        return self._parent_router

    @parent_router.setter
    def parent_router(self, router: Router) -> None:
        if not isinstance(router, Router):
            raise ValueError(
                f"router should be instance of Router not {type(router).__name__!r}"  # noqa: E501
            )
        if self._parent_router:
            raise RuntimeError(
                f"Router is already attached to {self._parent_router!r}"
            )
        if self is router:
            raise RuntimeError("Self-referencing routers is not allowed")

        parent: Router | None = router
        while parent is not None:
            if parent is self:
                raise RuntimeError(
                    "Circular referencing of Router is not allowed"
                )

            parent = parent.parent_router

        self._parent_router = router
        router._sub_routers.append(self)

    def include_router(
        self,
        router: Router,
        *,
        prefix: str | None = None,
        default_response_class: type[Response] | None = None,
    ) -> Router:
        if not isinstance(router, Router):
            raise ValueError(
                f"router should be instance of Router not {type(router).__name__!r}"  # noqa: E501
            )
        router.parent_router = self
        if prefix is not None:
            router.prefix = prefix
        if default_response_class is not None:
            router.default_response_class = default_response_class
        return router

    @property
    def chain_head(self) -> Iterable[Router]:
        router: Router | None = self
        while router is not None:
            yield router
            router = router.parent_router

    @property
    def chain_tail(self) -> Iterable[Router]:
        yield self
        for router in self._sub_routers:
            yield from router.chain_tail

    def __str__(self) -> str:
        return f"{type(self).__name__} {self.name!r}"

    def __repr__(self) -> str:
        return f"<{self}>"

    def url_path_for(self, name: str, /, **path_params: Any) -> str:
        for route in self.route:
            try:
                return route.url_path_for(name, **path_params)
            except NoMatchFound:
                pass
        raise NoMatchFound(name, path_params)

    def add_staticfiles(
        self,
        path: str,
        /,
        directory: str | PathLike | Sequence[str | PathLike],
        *,
        name: str = "static",
    ) -> None:
        if not path.startswith("/"):
            raise ValueError(f"Path {path!r} must start with '/'")
        if not path.endswith("/"):
            raise ValueError(f"Path {path!r} must end with '/'")

        path = path + "{path}" + "/"

        if not isinstance(directory, Sequence) or isinstance(directory, str):
            directory = [directory]

        directories = tuple(map(Path, directory))

        for directory in directories:
            if not directory.is_dir():
                raise NotADirectoryError(
                    f"Directory '{directory}' does not exist or is not a directory"
                )

        def callback(request: Request):
            for directory in directories:
                file_path = directory / request.path_params["path"]

                if not file_path.is_file():
                    return NOT_FOUND_RESPONSE

                response = FileResponse(file_path)

                if is_not_modified(request, response):
                    return NOT_MODIFIED_RESPONSE

                return response

        self.route.register(callback, path, name=name, method=HTTPMethod.GET)
        self.route.register(callback, path, method=HTTPMethod.HEAD)

    def outer_middleware(
        self, middleware: Middleware | None = None
    ) -> Callable[[Middleware], Middleware] | Middleware:
        return self.route.outer_middleware(middleware)

    def middleware(
        self, middleware: Middleware | None = None
    ) -> Callable[[Middleware], Middleware] | Middleware:
        return self.route.middleware(middleware)

    def filter(self, *filters: CallbackType) -> None:
        self.route.filter(*filters)

    def delete(
        self,
        path: str,
        /,
        *filters: CallbackType,
        name: str | None = None,
        status_code: int = HTTPStatus.OK,
        response_class: type[Response] | None = None,
        response_model: type | None = None,
    ) -> Callable[[CallbackType], CallbackType]:
        return self.route(
            path,
            *filters,
            name=name,
            method=HTTPMethod.DELETE,
            status_code=status_code,
            response_class=response_class,
            response_model=response_model,
        )

    def get(
        self,
        path: str,
        /,
        *filters: CallbackType,
        name: str | None = None,
        status_code: int = HTTPStatus.OK,
        response_class: type[Response] | None = None,
        response_model: type | None = None,
    ) -> Callable[[CallbackType], CallbackType]:
        return self.route(
            path,
            *filters,
            name=name,
            method=HTTPMethod.GET,
            status_code=status_code,
            response_class=response_class,
            response_model=response_model,
        )

    def head(
        self,
        path: str,
        /,
        *filters: CallbackType,
        name: str | None = None,
        status_code: int = HTTPStatus.OK,
        response_class: type[Response] | None = None,
        response_model: type | None = None,
    ) -> Callable[[CallbackType], CallbackType]:
        return self.route(
            path,
            *filters,
            name=name,
            method=HTTPMethod.HEAD,
            status_code=status_code,
            response_class=response_class,
            response_model=response_model,
        )

    def options(
        self,
        path: str,
        /,
        *filters: CallbackType,
        name: str | None = None,
        status_code: int = HTTPStatus.OK,
        response_class: type[Response] | None = None,
        response_model: type | None = None,
    ) -> Callable[[CallbackType], CallbackType]:
        return self.route(
            path,
            *filters,
            name=name,
            method=HTTPMethod.OPTIONS,
            status_code=status_code,
            response_class=response_class,
            response_model=response_model,
        )

    def patch(
        self,
        path: str,
        /,
        *filters: CallbackType,
        name: str | None = None,
        status_code: int = HTTPStatus.OK,
        response_class: type[Response] | None = None,
        response_model: type | None = None,
    ) -> Callable[[CallbackType], CallbackType]:
        return self.route(
            path,
            *filters,
            name=name,
            method=HTTPMethod.PATCH,
            status_code=status_code,
            response_class=response_class,
            response_model=response_model,
        )

    def post(
        self,
        path: str,
        /,
        *filters: CallbackType,
        name: str | None = None,
        status_code: int = HTTPStatus.OK,
        response_class: type[Response] | None = None,
        response_model: type | None = None,
    ) -> Callable[[CallbackType], CallbackType]:
        return self.route(
            path,
            *filters,
            name=name,
            method=HTTPMethod.POST,
            status_code=status_code,
            response_class=response_class,
            response_model=response_model,
        )

    def put(
        self,
        path: str,
        /,
        *filters: CallbackType,
        name: str | None = None,
        status_code: int = HTTPStatus.OK,
        response_class: type[Response] | None = None,
        response_model: type | None = None,
    ) -> Callable[[CallbackType], CallbackType]:
        return self.route(
            path,
            *filters,
            name=name,
            method=HTTPMethod.PUT,
            status_code=status_code,
            response_class=response_class,
            response_model=response_model,
        )

    def trace(
        self,
        path: str,
        /,
        *filters: CallbackType,
        name: str | None = None,
        status_code: int = HTTPStatus.OK,
        response_class: type[Response] | None = None,
        response_model: type | None = None,
    ) -> Callable[[CallbackType], CallbackType]:
        return self.route(
            path,
            *filters,
            name=name,
            method=HTTPMethod.TRACE,
            status_code=status_code,
            response_class=response_class,
            response_model=response_model,
        )
