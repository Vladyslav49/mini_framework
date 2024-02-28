import json
import keyword
import re
from collections.abc import Callable
from http.cookies import SimpleCookie
from typing import Any
from urllib.parse import parse_qsl
from wsgiref.types import WSGIEnvironment

from multidict import CIMultiDict

from mini_framework.datastructures import FormData, Address

try:
    import multipart
    from multipart.multipart import Field, File
except ImportError:
    multipart = None

PATH_PARAM_PATTERN = (
    r"{([^{}]+?)}"  # Pattern to find path parameters in the path template
)
COMPILED_PATH_PARAM_PATTERN = re.compile(PATH_PARAM_PATTERN)


class Request:
    __slots__ = (
        "_environ",
        "_body",
        "_json",
        "_query_params",
        "_path_params",
        "_multipart",
        "_headers",
        "_cookies",
    )

    def __init__(
        self, environ: WSGIEnvironment, *, path_params: dict[str, str]
    ) -> None:
        self._environ = environ
        self._path_params: dict[str, str] = path_params
        self._body: bytes | None = None
        self._json: Any | None = None
        self._query_params: dict[str, str | list[str]] | None = None
        self._multipart: FormData | None = None
        self._headers: CIMultiDict | None = None
        self._cookies: dict[str, str] | None = None

    @property
    def path(self) -> str:
        return ensure_trailing_slash(self._environ["PATH_INFO"])

    @property
    def method(self) -> str:
        return self._environ["REQUEST_METHOD"]

    @property
    def client(self) -> Address | None:
        host = self._environ.get("REMOTE_ADDR")
        port = self._environ.get("REMOTE_PORT")
        if host and port:
            return Address(host=host, port=port)
        return None

    @property
    def body(self) -> bytes:
        if self._body is None:
            self._body = self._environ["wsgi.input"].read()
        return self._body

    @property
    def text(self) -> str:
        return self.body.decode()

    @property
    def query_params(self) -> dict[str, str | list[str]]:
        if self._query_params is None:
            self._query_params = parse_query_params(
                self._environ.get("QUERY_STRING", ""),
            )
        return self._query_params

    @property
    def path_params(self) -> dict[str, str]:
        return self._path_params

    @property
    def headers(self) -> CIMultiDict:
        if self._headers is None:
            self._headers = extract_headers(self._environ)
        return self._headers

    @property
    def cookies(self) -> dict[str, str]:
        if self._cookies is None:
            self._cookies = cookie_parser(
                self._environ.get("HTTP_COOKIE", ""),
            )
        return self._cookies

    def json(self, loads: Callable[..., Any] = json.loads) -> Any:
        if self._json is None:
            self._json = loads(self.text)
        return self._json

    def form(self, *, chunk_size: int = 1048576) -> FormData:
        if self._multipart is None:
            assert multipart is not None, "python-multipart is not installed"

            fields: list["Field"] = []
            files: list["File"] = []

            self._environ["wsgi.input"].seek(0)

            multipart.parse_form(
                headers=self.headers,
                input_stream=self._environ["wsgi.input"],
                on_field=fields.append,
                on_file=files.append,
                chunk_size=chunk_size,
            )

            self._multipart = FormData(fields=fields, files=files)
        return self._multipart


def ensure_trailing_slash(path: str) -> str:
    if path[-1] == "/":
        return path
    return path + "/"


def parse_query_params(query_string: str) -> dict[str, str | list[str]]:
    parsed_result = {}
    pairs = parse_qsl(query_string, keep_blank_values=True)
    for name, value in pairs:
        if name not in parsed_result:
            parsed_result[name] = value
        elif isinstance(parsed_result[name], list):
            parsed_result[name].append(value)
        else:
            parsed_result[name] = [parsed_result[name], value]
    return parsed_result


def extract_headers(environ: WSGIEnvironment) -> CIMultiDict:
    headers = CIMultiDict()
    for key, value in environ.items():
        if key.startswith("HTTP_"):
            headers[key[5:].replace("_", "-").title()] = value
        elif key in ("CONTENT_TYPE", "CONTENT_LENGTH"):
            headers[key.replace("_", "-").title()] = value
    return headers


def extract_path_params_from_template(path: str) -> list[str]:
    params = COMPILED_PATH_PARAM_PATTERN.findall(path)

    if not params:
        return []

    _validate_path_params(path, params)
    _validate_path(path, params)

    return params


def _validate_path_params(path: str, params: list[str]) -> None:
    if len(params) != len(set(params)):
        raise ValueError(f"Invalid path: {path!r}. Parameters must be unique")

    for param in params:
        if not param.isidentifier():
            raise ValueError(
                f"Invalid path: {path!r}. "
                f"Parameter name {param!r} is not a valid Python identifier"
            )
        if keyword.iskeyword(param):
            raise ValueError(
                f"Invalid path: {path!r}. "
                f"Parameter name {param!r} is a Python keyword"
            )


def _validate_path(path: str, params: list[str]) -> None:
    try:
        path = path.format_map({param: "1" for param in params})
    except ValueError:
        raise ValueError(f"Invalid path: {path!r}") from None

    if ("{" in path) or ("}" in path):
        raise ValueError(f"Invalid path: {path!r}")


def extract_path_params(path_template: str, path: str) -> dict[str, str]:
    parts = path_template.strip("/").split("/")

    if parts == [""]:
        return {}

    values = path.strip("/").split("/")

    if len(parts) != len(values):
        raise ValueError(
            f"Invalid path: {path!r}. Expected {len(parts)} parts, got {len(values)}"  # noqa: E501
        )

    params: dict[str, str] = {}

    for part, value in zip(parts, values):
        if part != value:
            if match := COMPILED_PATH_PARAM_PATTERN.match(part):
                param = match.group(1)
                params[param] = value
            else:
                raise ValueError(
                    f"Invalid path: {path!r}. Expected {part!r}, got {value!r}"
                )

    return params


def cookie_parser(cookie_string: str) -> dict[str, str]:
    if not cookie_string:
        return {}

    cookies = SimpleCookie(cookie_string)
    return {key: cookie.value for key, cookie in cookies.items()}
