from mini_framework.exceptions import HTTPException
from mini_framework.responses import Response


def http_exception_handler(exception: HTTPException) -> Response:
    return exception.response_class(
        exception.detail,
        headers=exception.headers,
        status_code=exception.status_code,
    )
