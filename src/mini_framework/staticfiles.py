from collections.abc import Sequence
from email.utils import parsedate
from http import HTTPStatus
from os import PathLike
from pathlib import Path
from typing import Final, Annotated

from mini_framework import params
from mini_framework.request import Request
from mini_framework.responses import Response, FileResponse, JSONResponse

NOT_FOUND_RESPONSE: Final[JSONResponse] = JSONResponse(
    {"detail": HTTPStatus.NOT_FOUND.phrase},
    status_code=HTTPStatus.NOT_FOUND,
)

NOT_MODIFIED_RESPONSE: Final[Response] = Response(
    content=None, status_code=HTTPStatus.NOT_MODIFIED
)


class StaticFiles:
    __slots__ = ("_directories",)

    def __init__(
        self, *, directory: str | PathLike | Sequence[str | PathLike]
    ) -> None:
        if not isinstance(directory, Sequence) or isinstance(directory, str):
            directory = [directory]

        directories = tuple(map(Path, directory))

        for directory in directories:
            if not directory.is_dir():
                raise NotADirectoryError(
                    f"Directory {str(directory)!r} does not exist or is not a directory"
                )

        self._directories = directories

    def callback(self, request: Request, path: Annotated[str, params.Path()]):
        for directory in self._directories:
            file_path = directory / path

            if not file_path.is_file():
                return NOT_FOUND_RESPONSE

            response = FileResponse(file_path)

            if _is_not_modified(request, response):
                return NOT_MODIFIED_RESPONSE

            return response


def _is_not_modified(request: Request, response: Response) -> bool:
    if_none_match = request.headers.get("if-none-match")
    etag = response.headers.get("etag")
    if (
        if_none_match is not None
        and etag is not None
        and if_none_match == etag
    ):
        return True

    if_modified_since = parsedate(request.headers.get("if-modified-since"))
    last_modified = parsedate(response.headers.get("last-modified"))
    return (
        if_modified_since is not None
        and last_modified is not None
        and if_modified_since >= last_modified
    )
