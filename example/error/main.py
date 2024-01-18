from http import HTTPStatus

from mini_framework import Application
from mini_framework.filters.exception import ExceptionTypeFilter
from mini_framework.responses import PlainTextResponse

app = Application()


@app.error(ExceptionTypeFilter(Exception))
def exception_handler():
    return PlainTextResponse(
        "Something went wrong",
        status_code=HTTPStatus.INTERNAL_SERVER_ERROR,
    )


@app.get("/")
def index():
    raise Exception("Something went wrong")
