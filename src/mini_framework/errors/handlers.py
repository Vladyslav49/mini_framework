from http import HTTPStatus

from mini_framework.exceptions import HTTPException, RequestValidationError
from mini_framework.responses import JSONResponse


def http_exception_handler(exception: HTTPException) -> JSONResponse:
    return JSONResponse(
        {"detail": exception.detail},
        status_code=exception.status_code,
        headers=exception.headers,
    )


def request_validation_error_handler(
    exception: RequestValidationError,
) -> JSONResponse:
    return JSONResponse(
        {"detail": exception.detail},
        status_code=HTTPStatus.UNPROCESSABLE_ENTITY,
    )
