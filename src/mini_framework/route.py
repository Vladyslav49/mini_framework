from collections.abc import Callable
from dataclasses import dataclass, field
from http import HTTPStatus
from typing import Any, TypeAlias

from mini_framework.filters import BaseFilter

Callback: TypeAlias = Callable[..., Any]


@dataclass(frozen=True, slots=True, kw_only=True)
class Route:
    callback: Callback
    path: str
    method: str
    status_code: int = HTTPStatus.OK
    filters: list[BaseFilter] = field(default_factory=list)

    def __post_init__(self):
        if not self.path.startswith("/"):
            raise ValueError(f"Path {self.path!r} must start with '/'")
        if not self.path.endswith("/"):
            raise ValueError(f"Path {self.path!r} must end with '/'")
        for filter in self.filters:
            if not isinstance(filter, BaseFilter):
                raise TypeError(
                    f"Filter {filter!r} must be an instance of BaseFilter",
                )

    def check(self) -> bool:
        if not self.filters:
            return True
        for filter in self.filters:
            if not filter():
                return False
        return True
