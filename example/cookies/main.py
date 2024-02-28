from http import HTTPStatus
from typing import Annotated

from mini_framework import Application
from mini_framework.params import Cookie
from mini_framework.request import Request
from mini_framework.responses import JSONResponse, PlainTextResponse

app = Application()


@app.get("/cookies/")
def cookies(request: Request) -> dict[str, str]:
    return request.cookies


@app.get(
    "/set-cookies/",
    status_code=HTTPStatus.CREATED,
    response_class=PlainTextResponse,
)
def set_cookies(response: PlainTextResponse) -> str:
    response.set_cookie("name", "John")
    response.set_cookie("age", "20", httponly=True)
    return "Cookies set"


@app.get("/clear-cookie-name/", response_class=PlainTextResponse)
def clear_cookies(response: PlainTextResponse) -> str:
    response.delete_cookie("name")
    return "Cookies cleared"


@app.get("/age/")
def age(age: Annotated[str, Cookie()]):
    return JSONResponse({"age": age})
