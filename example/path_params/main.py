from typing import Annotated

from mini_framework import Application
from mini_framework.params import Path
from mini_framework.request import Request
from mini_framework.responses import PlainTextResponse

app = Application()


@app.get("/hello/world/")
def hello_world():
    return PlainTextResponse("Hello!")


@app.get("/hello/{name}/{from_user}/")
def hello_from_user_with_path_params(request: Request):
    name = request.path_params["name"].capitalize()
    from_user = request.path_params["from_user"].capitalize()
    return PlainTextResponse(f"Hello, {name} from {from_user}!")


@app.get("/hello/{name}/")
def hello_with_path_params(name: Annotated[str, Path()]):
    return PlainTextResponse(f"Hello, {name.capitalize()}!")


@app.get("/hello/")
def hello():
    return PlainTextResponse("Hello, Anonymous!")
