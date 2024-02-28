from dataclasses import dataclass
from typing import Annotated

from mini_framework import Application
from mini_framework.params import Body, BodyModel
from mini_framework.request import Request
from mini_framework.responses import JSONResponse, PlainTextResponse

app = Application()


@app.post("/")
def index(request: Request):
    json = request.json()
    return JSONResponse(json)


@app.post("/hello/")
def hello(name: Annotated[str, Body()]):
    return PlainTextResponse(f"Hello, {name}!")


@dataclass(frozen=True, slots=True, kw_only=True)
class User:
    name: str
    age: int


@app.post("/user/")
def user(model: Annotated[User, BodyModel()]) -> User:
    return model


@app.post("/user-embeded/")
def user_embeded(user: Annotated[User, BodyModel(embed=True)]) -> User:
    return user


@app.post("/user-with-id/")
def user_with_id(
    id: Annotated[int, Body()], user: Annotated[User, BodyModel()]
):
    return {"id": id, "user": user}


@dataclass(frozen=True, slots=True, kw_only=True)
class Home:
    owner: User
    address: str
    square_footage: float
    num_rooms: int


@app.post("/home/")
def home(model: Annotated[Home, BodyModel()]) -> Home:
    return model
