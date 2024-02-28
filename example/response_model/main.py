from pydantic import BaseModel, ConfigDict

from mini_framework import Application

app = Application()


class User(BaseModel):
    model_config = ConfigDict(frozen=True)

    name: str
    age: int


@app.get("/", response_model=list[User])
def index() -> list[dict[str, str | int]]:
    return [
        {"name": "Dio", "age": 124},
        {"name": "Jotaro", "age": 17},
    ]
