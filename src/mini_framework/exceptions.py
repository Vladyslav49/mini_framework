from collections.abc import Mapping
from http import HTTPStatus

from mini_framework.responses import PlainTextResponse, Response


class FrameworkError(Exception):
    """Base class for all framework-related errors."""


class HTTPException(FrameworkError):
    def __init__(
        self,
        *,
        status_code: int,
        detail: str | None = None,
        headers: Mapping[str, str] | None = None,
        response_class: type[Response] = PlainTextResponse,
    ) -> None:
        if detail is None:
            detail = HTTPStatus(status_code).phrase
        self.status_code = status_code
        self.detail = detail
        self.headers = headers
        self.response_class = response_class

    def __repr__(self) -> str:
        return f"{type(self).__name__}(status_code={self.status_code!r}, detail={self.detail!r})"  # noqa: E501
