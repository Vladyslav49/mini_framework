from collections.abc import Callable
from dataclasses import dataclass
from http import HTTPMethod, HTTPStatus
from typing import Any


@dataclass(frozen=True, slots=True, kw_only=True)
class Route:
    handler: Callable[[], Any]
    path: str
    method: HTTPMethod | str
    status_code: int = HTTPStatus.OK

    def __post_init__(self):
        if not self.path.startswith("/"):
            raise ValueError("Path must start with '/'")
