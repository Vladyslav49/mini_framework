from collections.abc import Callable
from dataclasses import dataclass
from http import HTTPMethod, HTTPStatus
from typing import Any, TypeAlias

Handler: TypeAlias = Callable[[], Any]

SUPPORTED_METHODS: tuple[HTTPMethod, ...] = (
    HTTPMethod.GET,
    HTTPMethod.POST,
    HTTPMethod.PUT,
    HTTPMethod.PATCH,
    HTTPMethod.DELETE,
)


@dataclass(frozen=True, slots=True, kw_only=True)
class Route:
    handler: Handler
    path: str
    method: HTTPMethod | str
    status_code: int = HTTPStatus.OK

    def __post_init__(self):
        if not self.path.startswith("/"):
            raise ValueError(f"Path {self.path!r} must start with '/'")
        if self.method not in SUPPORTED_METHODS:
            raise ValueError(f"Method {self.method!r} is not supported")
