from dataclasses import dataclass, field
from collections.abc import Mapping
from http import HTTPStatus
from http.client import responses
from typing import Any


class FrameworkError(Exception):
    """Base class for all framework-related errors"""


@dataclass(kw_only=True)
class HTTPException(FrameworkError):
    status_code: int
    detail: Any | None = None
    headers: Mapping[str, str] | None = field(default=None, repr=False)

    def __post_init__(self) -> None:
        if self.status_code not in responses:
            raise ValueError(f"Invalid status code: {self.status_code}")
        if self.detail is None:
            self.detail = HTTPStatus(self.status_code).phrase

    def __str__(self) -> str:  # pragma: no cover
        return repr(self)


@dataclass
class _ValidationError(ValueError):
    detail: Any
    expected_type: type = field(kw_only=True)


@dataclass
class RequestValidationError(_ValidationError):
    params: Any = field(kw_only=True)


@dataclass
class ResponseValidationError(_ValidationError):
    value: Any = field(kw_only=True)
