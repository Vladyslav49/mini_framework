from collections.abc import Mapping
from http import HTTPStatus
from typing import Any


class Response:
    __slots__ = ("body", "status_code", "headers", "media_type", "charset")

    def __init__(
        self,
        content: Any,
        *,
        status_code: int = HTTPStatus.OK,
        headers: Mapping[str, str] | None = None,
        media_type: str | None = None,
        charset: str = "utf-8",
    ) -> None:
        self.status_code = status_code
        self.headers = headers or {}
        self.media_type = media_type
        self.charset = charset
        self.body = self.render(content)

    def render(self, content: Any) -> bytes:
        if content is None:
            return b""
        if isinstance(content, bytes):
            return content
        return content.encode(self.charset)  # type: ignore


class PlainTextResponse(Response):
    __slots__ = ()

    def __init__(
        self,
        content: Any,
        *,
        status_code: int = HTTPStatus.OK,
        headers: Mapping[str, str] | None = None,
        media_type: str | None = None,
        charset: str = "utf-8",
    ) -> None:
        if media_type is None:
            media_type = "text/plain"
        super().__init__(
            content,
            status_code=status_code,
            headers=headers,
            media_type=media_type,
            charset=charset,
        )


class HTMLResponse(Response):
    __slots__ = ()

    def __init__(
        self,
        content: Any,
        *,
        status_code: int = HTTPStatus.OK,
        headers: Mapping[str, str] | None = None,
        media_type: str | None = None,
        charset: str = "utf-8",
    ) -> None:
        if media_type is None:
            media_type = "text/html"
        super().__init__(
            content,
            status_code=status_code,
            headers=headers,
            media_type=media_type,
            charset=charset,
        )
