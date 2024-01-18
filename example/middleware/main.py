from typing import Any

from mini_framework import Application
from mini_framework.middlewares.base import CallNext
from mini_framework.responses import PlainTextResponse

app = Application()


@app.outer_middleware
def outer_middleware(call_next: CallNext, data: dict[str, Any]) -> Any:
    return call_next(data)


@app.middleware
def middleware(call_next: CallNext, data: dict[str, Any]) -> Any:
    return call_next(data)


@app.get("/")
def index():
    return PlainTextResponse("Hello, World!")
