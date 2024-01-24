from collections.abc import Callable
from dataclasses import dataclass, field
from functools import partial
from http import HTTPMethod
from typing import Any, TypeAlias

from mini_framework.filters import BaseFilter
from mini_framework.request import Request
from mini_framework.utils import prepare_kwargs

Callback: TypeAlias = Callable[..., Any]
Filter: TypeAlias = BaseFilter | Callable[..., dict[str, Any] | bool]


@dataclass(frozen=True, slots=True, kw_only=True)
class Route:
    callback: Callback
    path: str
    method: str
    filters: list[Filter] = field(default_factory=list)
    path_params: list[str] = field(default_factory=list)

    def __post_init__(self):
        if not self.path.startswith("/"):
            raise ValueError(f"Path {self.path!r} must start with '/'")
        if not self.path.endswith("/"):
            raise ValueError(f"Path {self.path!r} must end with '/'")
        if self.method not in tuple(HTTPMethod):
            raise ValueError(
                f"Method {self.method!r} is not valid HTTP method"
            )

    def match(self, request: Request) -> bool:
        if request.method != self.method:
            return False
        if not request.path_params:
            return self.path == request.path
        try:
            return request.path == self.path.format_map(request.path_params)
        except KeyError:  # occurs when path_params do not match
            return False

    def check(self, **kwargs: Any) -> tuple[bool, dict[str, Any]]:
        if not self.filters:
            return True, kwargs
        for filter in self.filters:
            if kwargs := prepare_kwargs(filter, kwargs):
                filter = partial(filter, **kwargs)
            check = filter()
            if not check:
                return False, kwargs
            if isinstance(check, dict):
                kwargs.update(check)
        return True, kwargs
