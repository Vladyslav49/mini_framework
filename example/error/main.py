from http import HTTPStatus

from mini_framework import Application
from mini_framework.exceptions import HTTPException
from mini_framework.filters.exception import HTTPExceptionStatusCodeFilter
from mini_framework.responses import PlainTextResponse

app = Application()


@app.error(HTTPExceptionStatusCodeFilter(HTTPStatus.INTERNAL_SERVER_ERROR))
def exception_handler(exception: HTTPException):
    return PlainTextResponse(
        content="Something went wrong", status_code=exception.status_code
    )


@app.get("/")
def index():
    raise HTTPException(status_code=HTTPStatus.INTERNAL_SERVER_ERROR)
