from typing import Any

from mini_framework import Application
from mini_framework.middlewares.base import CallNext
from mini_framework.responses import PlainTextResponse

app = Application(some_data="some_data")
app["some_value"] = 0


@app.outer_middleware
def outer_middleware(call_next: CallNext, data: dict[str, Any]) -> Any:
    data["outer_middleware_data"] = "outer_middleware_data"
    return call_next(data)


@app.middleware
def middleware(call_next: CallNext, data: dict[str, Any]) -> Any:
    data["middleware_data"] = "middleware_data"
    return call_next(data)


@app.get("/")
def index(
    some_data: str,
    some_value: int,
    outer_middleware_data: str,
    middleware_data: str,
):
    return PlainTextResponse("Hello, World!")


@app.get("/hello/{name}/")
def hello(name: str):
    return PlainTextResponse(f"Hello, {name}!")
