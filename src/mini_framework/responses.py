from collections.abc import Mapping
from http import HTTPStatus
from typing import Any


class Response:
    def __init__(
        self,
        content: Any,
        *,
        status_code: int = HTTPStatus.OK,
        headers: Mapping[str, str] | None = None,
        media_type: str | None = None,
        charset: str = "utf-8",
    ) -> None:
        self.content = content
        self.status_code = status_code
        self.headers = headers or {}
        self.media_type = media_type
        self.charset = charset

    def render(self) -> bytes:
        raise NotImplementedError


class PlainTextResponse(Response):
    def __init__(
        self,
        content: Any,
        *,
        status_code: int = HTTPStatus.OK,
        headers: Mapping[str, str] | None = None,
        charset: str = "utf-8",
    ) -> None:
        super().__init__(
            content=content,
            status_code=status_code,
            headers=headers,
            media_type="text/plain",
            charset=charset,
        )

    def render(self) -> bytes:
        return str(self.content).encode(self.charset)
