import hashlib
import os
import json
from collections.abc import Mapping, Iterable
from datetime import datetime
from email.utils import format_datetime, formatdate
from http import HTTPStatus
from http.client import responses
from http.cookies import BaseCookie, SimpleCookie
from mimetypes import guess_type
from os import PathLike
from typing import Any, Literal
from urllib.parse import quote

from multidict import CIMultiDict


class Response:
    __slots__ = (
        "status_code",
        "headers",
        "media_type",
        "charset",
        "content",
    )

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
        self.content = content

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

    def render(self) -> bytes:
        if self.content is None:
            return b""
        if isinstance(self.content, bytes):
            return self.content
        return self.content.encode(self.charset)


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

    def render(self) -> bytes:
        return json.dumps(
            self.content,
            ensure_ascii=False,
            allow_nan=False,
            indent=None,
            separators=(",", ":"),
        ).encode(self.charset)


class RedirectResponse(Response):
    __slots__ = ()

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


class StreamingResponse(Response):
    __slots__ = ("body_iterator",)

    def __init__(
        self,
        content: Iterable[bytes],
        *,
        status_code: int = HTTPStatus.OK,
        headers: Mapping[str, str] | None = None,
        media_type: str | None = None,
    ) -> None:
        super().__init__(
            content=b"",
            status_code=status_code,
            headers=headers,
            media_type=media_type,
        )
        self.body_iterator = iter(content)


class FileResponse(Response):
    __slots__ = ("path", "filename", "stat_result")

    chunk_size = 64 * 1024

    def __init__(
        self,
        path: str | PathLike[str],
        *,
        status_code: int = HTTPStatus.OK,
        headers: Mapping[str, str] | None = None,
        media_type: str | None = None,
        filename: str | None = None,
        stat_result: os.stat_result | None = None,
        content_disposition_type: str = "attachment",
    ) -> None:
        if not os.path.exists(path):
            raise FileNotFoundError(f"File '{path}' not found")
        if not os.path.isfile(path):
            raise ValueError(f"'{path}' is not a valid file path")
        super().__init__(
            content=b"",
            status_code=status_code,
            headers=headers,
            media_type=media_type,
        )
        self.path = path
        self.status_code = status_code
        self.filename = filename
        if media_type is None:
            media_type = guess_type(filename or path)[0] or "text/plain"
        self.media_type = media_type

        content_disposition_filename = filename or os.path.basename(path)
        content_disposition = '{}; filename="{}"'.format(
            content_disposition_type, content_disposition_filename
        )
        self.headers.setdefault("Content-Disposition", content_disposition)

        self.stat_result = stat_result or os.stat(path)
        self.set_stat_headers()

    def set_stat_headers(self) -> None:
        content_length = str(self.stat_result.st_size)
        last_modified = formatdate(self.stat_result.st_mtime, usegmt=True)
        etag_base = (
            str(self.stat_result.st_mtime)
            + "-"
            + str(self.stat_result.st_size)
        )
        etag = f'"{hashlib.md5(etag_base.encode(), usedforsecurity=False).hexdigest()}"'

        self.headers.setdefault("Content-Length", content_length)
        self.headers.setdefault("Last-Modified", last_modified)
        self.headers.setdefault("Etag", etag)

    def iter_content(self) -> Iterable[bytes]:
        with open(self.path, mode="rb") as file:
            while chunk := file.read(self.chunk_size):
                yield chunk


def get_status_code_and_phrase(status_code: int) -> str:
    if status_code not in responses:
        raise ValueError(f"Invalid status code: {status_code}")
    return f"{status_code} {responses[status_code]}"


def prepare_headers(response: Response, body: bytes) -> list[tuple[str, str]]:
    response.headers.setdefault(
        "Content-Type", f"{response.media_type}; charset={response.charset}"
    )
    if not isinstance(response, (StreamingResponse, FileResponse)):
        response.headers.setdefault("Content-Length", str(len(body)))
    return list(response.headers.items())
