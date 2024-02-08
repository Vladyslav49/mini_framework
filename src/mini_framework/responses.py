import json
from collections.abc import Mapping
from datetime import datetime
from email.utils import format_datetime
from http import HTTPStatus
from http.client import responses
from http.cookies import BaseCookie, SimpleCookie
from typing import Any, Literal
from urllib.parse import quote

from multidict import CIMultiDict


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
        if headers is None:
            headers = {}
        self.headers = CIMultiDict(headers)
        self.media_type = media_type
        self.charset = charset
        self.body = self.render(content)

    def set_cookie(
        self,
        key: str,
        value: str = "",
        max_age: int | None = None,
        expires: datetime | str | int | None = None,
        path: str = "/",
        domain: str | None = None,
        secure: bool = False,
        httponly: bool = False,
        samesite: Literal["lax", "strict", "none"] | None = "lax",
    ) -> None:
        cookie: BaseCookie[str] = SimpleCookie()
        cookie[key] = value
        if max_age is not None:
            cookie[key]["max-age"] = max_age
        if expires is not None:
            if isinstance(expires, datetime):
                cookie[key]["expires"] = format_datetime(expires, usegmt=True)
            else:
                cookie[key]["expires"] = expires
        if path is not None:
            cookie[key]["path"] = path
        if domain is not None:
            cookie[key]["domain"] = domain
        if secure:
            cookie[key]["secure"] = True
        if httponly:
            cookie[key]["httponly"] = True
        if samesite is not None:
            assert samesite.lower() in [
                "strict",
                "lax",
                "none",
            ], "samesite must be either 'strict', 'lax' or 'none'"
            cookie[key]["samesite"] = samesite
        cookie_val = cookie.output(header="").strip()
        self.headers.add("Set-Cookie", cookie_val)

    def delete_cookie(
        self,
        key: str,
        path: str = "/",
        domain: str | None = None,
        secure: bool = False,
        httponly: bool = False,
        samesite: Literal["lax", "strict", "none"] | None = "lax",
    ) -> None:
        self.set_cookie(
            key,
            max_age=0,
            expires=0,
            path=path,
            domain=domain,
            secure=secure,
            httponly=httponly,
            samesite=samesite,
        )

    def render(self, content: Any) -> bytes:
        if content is None:
            return b""
        if isinstance(content, bytes):
            return content
        return content.encode(self.charset)


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


class JSONResponse(Response):
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
            media_type = "application/json"
        super().__init__(
            content,
            status_code=status_code,
            headers=headers,
            media_type=media_type,
            charset=charset,
        )

    def render(self, content: Any) -> bytes:
        return json.dumps(
            content,
            ensure_ascii=False,
            allow_nan=False,
            indent=None,
            separators=(",", ":"),
        ).encode(self.charset)


class RedirectResponse(Response):
    def __init__(
        self,
        url: str,
        *,
        status_code: int = HTTPStatus.TEMPORARY_REDIRECT,
        headers: Mapping[str, str] | None = None,
    ) -> None:
        super().__init__(
            content=b"",
            status_code=status_code,
            headers=headers,
        )
        self.headers["location"] = quote(url, safe=":/%#?=@[]!$&'()*+,;")


def get_status_code_and_phrase(status_code: int) -> str:
    """Get status code and phrase for a given status code."""
    if status_code not in responses:
        raise ValueError(f"Invalid status code: {status_code}")
    return f"{status_code} {responses[status_code]}"


def prepare_headers(response: Response) -> list[tuple[str, str]]:
    """Prepare headers for a given response."""
    response_cookies = SimpleCookie()

    for cookie in response.headers.getall("Set-Cookie", ()):
        response_cookies.load(cookie)

    headers = [
        ("Content-Type", f"{response.media_type}; charset={response.charset}"),
        ("Content-Length", str(len(response.body))),
    ]

    return list(response.headers.items()) + headers
