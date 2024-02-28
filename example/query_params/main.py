from typing import Annotated

from mini_framework import Application
from mini_framework.params import Query
from mini_framework.request import Request
from mini_framework.responses import PlainTextResponse

app = Application()


@app.get("/")
def index(request: Request):
    name = request.query_params.get("name", "Anonymous")
    return PlainTextResponse(f"Hello, {name}!")


@app.get("/hello/")
def hello(name: Annotated[str, Query()] = "Anonymous"):
    return PlainTextResponse(f"Hello, {name}!")


@app.get("/greetings/")
def greetings(names: Annotated[list[str], Query()]):
    return PlainTextResponse(f"Hello, {', '.join(names)}!")
