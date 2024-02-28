from http import HTTPStatus
from typing import Annotated

from pydantic import BaseModel, ConfigDict, Field

from mini_framework import Application
from mini_framework.exceptions import RequestValidationError
from mini_framework.filters.exception import ExceptionTypeFilter
from mini_framework.params import Query
from mini_framework.responses import JSONResponse

app = Application()


class User(BaseModel):
    model_config = ConfigDict(frozen=True)

    name: str
    age: int


@app.get("/")
def index(
    name: Annotated[str, Query()], age: Annotated[int, Query(), Field(ge=18)]
) -> User:
    return User(name=name, age=age)


@app.error(ExceptionTypeFilter(RequestValidationError))
def exception_handler(exception: RequestValidationError) -> JSONResponse:
    return JSONResponse(
        {"detail": exception.detail, "hi": "Hello, World!"},
        status_code=HTTPStatus.UNPROCESSABLE_ENTITY,
    )
