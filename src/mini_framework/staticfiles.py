from email.utils import parsedate

from mini_framework.request import Request
from mini_framework.responses import Response


def is_not_modified(request: Request, response: Response) -> bool:
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
